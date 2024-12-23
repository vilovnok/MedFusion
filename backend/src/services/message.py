from ..utils.unitofwork import IUnitOfWork
from ..schemas.messages import *
from ..schemas.user import *
from ..models.user import User
from ..models.messages import Message as Core
from fastapi import HTTPException
from agent.src import MedFusionLLM
from agent.src.utils import ModelType


class MessageService:
    async def generate(self, uow: IUnitOfWork, data: Message, limit:int):
        async with uow:

            checker = await uow.user.get_one(id=data.user_id, n_tab=0)
            if not checker:
                raise HTTPException(status_code=404, detail='Пользователь не найден.')

            token = checker.token
            model_name = 'mistral-large-latest mistral-large-2411 mistral-large-2407 mistral-large-2402'.split()         
            messages = await uow.message.get_all(n_tab=0, user_id=int(data.user_id))               
            chat_history = "\n".join([(f'Human: {message.human_text.strip()}\nAI: {message.ai_text.strip()}\n{message.full_metadata}') for message in messages[-limit:]])            
            
            print('\n')
            print(f'Chat history: {[chat_history]}')
            print('\n')
            
            for model in model_name:
                agent = MedFusionLLM(model_type=ModelType.MISTRAL, token=token, model_name=model)

                response, full_metadata = agent.invoke(user_input=data.text, chat_history=chat_history)
                if full_metadata:
                    full_metadata = "\n".join([f'[{title}][{link}]-{date}' for title, _, date, link in full_metadata])
                    full_metadata = f'**Ссылки** \n{full_metadata}'
                else:
                    full_metadata = None
                
                errors_to_ignore = ['Error response 401', 'Error response 429']                
                if any(error in response for error in errors_to_ignore):
                    continue
                break

            if not response or 'Error response 401' in response:
                raise HTTPException(status_code=400, detail="Ответ от модели пустой или некорректный.")
            
            try:
                user_model = MessageCreate(
                    user_id=data.user_id,
                    human_text=data.text,
                    ai_text=response,
                    full_metadata=full_metadata
                )         
                await uow.message.add_one(user_model.model_dump(), n_tab=0)  
                await uow.commit()

                if response.find('**Ссылки**'):
                    response = response[:response.find('**Ссылки**')]
                
                return {'role':'ai','ai_text': response, 'full_metadata':full_metadata}
            except Exception as err:
                await uow.rollback()
                raise HTTPException(status_code=400, detail="Ошибка при добавлении сообщения в БД.")
        
    async def check_token(self, uow: IUnitOfWork, data: Message):
        async with uow:

            token = data.token     
            if not token:
                raise HTTPException(status_code=404, detail='Токен не найден.')        
                        
            agent = MedFusionLLM(model_type=ModelType.MISTRAL, api_key=f'{token}', token=token, max_tokens=20)
            test_prompt = "выведи одно слово"
            response, full_metadata = agent.invoke(test_prompt)
            
            errors_to_ignore = ['error response 401', 'error response 429']                
            if any(error in f'{response}'.lower() for error in errors_to_ignore):
                raise HTTPException(status_code=401, detail='ТОкен не действиетлен.')
            
            try:
                retriever_response = agent.test_retriever('кровь')
                print(retriever_response)
            except Exception as e:
                print(f'Retriever dead: {e}')
            
            await uow.user.update(where=[User.id==int(data.user_id)], n_tab=0, values={'token': token})            
            await uow.commit()
            if response:
                return {
                    "message": "Модель подключена и работает корректно.",
                    "status": "success",
                    "token":token
                }
            else:
                raise HTTPException(status_code=400, detail="Лимит вашего токена истек.")
            
    async def get_messages(self, uow: IUnitOfWork, data: MessageCreate):
        async with uow:
            checker = await uow.user.get_one(id=data.user_id, n_tab=0)
            if not checker:
                raise HTTPException(status_code=404, detail='Пользователь не найден.')
            try:
                messages = await uow.message.get_all(n_tab=0, user_id=int(data.user_id))
                messages_post = MessageReadAll(**data.model_dump(), posts=messages)                        
            
            except Exception as err:
                raise HTTPException(status_code=400, detail="Что-то не так с вашеми данными.")            

            if messages_post:
                return {
                    "message": "Модель подключена и работает корректно.",
                    "status": "success",
                    "messages": messages_post
                }
            else:
                raise HTTPException(status_code=400, detail="Лимит вашего токена истек.")
            
    async def get_liked(self, uow: IUnitOfWork, data: Message):
        async with uow:
            try:
                liked = data.liked
                checker = await uow.user.get_one(id=int(data.user_id), n_tab=0)

                if not checker:
                    raise HTTPException(status_code=404, detail='Такого пользователя не существует!')        

                await uow.message.update(where=[User.id==int(data.user_id), Core.ai_text==data.text], n_tab=0, values={'liked': liked})            
                await uow.commit()

                return {
                    "status": "success",
                    "message":'Оценка пользователя получена.'
                }
            except Exception as err:
                await uow.rollback()
                raise HTTPException(status_code=400, detail="Ошибка при изменении лайка.")
            
    async def clear_chat(self, uow: IUnitOfWork, data: Message):
        async with uow:
            try:
                await uow.message.delete(user_id=int(data.user_id), n_tab=0)
                await uow.commit()

                return {
                    "status": "success",
                    "message":'Чат очищен!'
                }
            except Exception as err:
                await uow.rollback()
                raise HTTPException(status_code=400, detail="Ошибка при изменении db.")