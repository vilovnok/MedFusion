from ..utils.unitofwork import IUnitOfWork
from ..schemas.messages import *
from ..schemas.user import *
from ..models.user import User
from ..models.messages import Message as Core
from ..models.messages import Metrics

from fastapi import HTTPException
from agent.src import MedFusionLLM
from agent.src.utils import ModelType


class MessageService:
    

    def check_inf(self, token: str):
        try:
            agent = MedFusionLLM(model_type=ModelType.MISTRAL, api_key=token, token=token)            
            response, _ = agent.invoke("выведи одно слово")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Ошибка в Rag-system: {str(e)}')        
        
        errors_to_ignore = ['error response 401', 'error response 429']                
        if any(error in f'{response}'.lower() for error in errors_to_ignore):
            raise HTTPException(status_code=401, detail='ТОкен не действиетлен.')
        
        return response

    async def generate(self, uow: IUnitOfWork, data: Message, limit:int):
        async with uow:

            checker = await uow.user.get_one(id=data.user_id, n_tab=0)
            if not checker:
                raise HTTPException(status_code=404, detail='Пользователь не найден.')

            token = checker.token
            model_names = 'mistral-large-latest mistral-large-2411 mistral-large-2407 mistral-large-2402'.split()         
            messages = await uow.message.get_all(n_tab=0, user_id=int(data.user_id))               
            chat_history = "\n".join([(f'Human: {message.human_text.strip()}\nAI: {message.ai_text.strip()}\n{message.full_metadata}') for message in messages[-limit:]])            
            
            print('\n')
            print(f'Chat history: {[chat_history]}')
            print('\n')
            
            for model_name in model_names:

                agent = MedFusionLLM(model_type=ModelType.MISTRAL, token=token, model_name=model_name)
                response, full_metadata = agent.invoke(user_input=data.text, chat_history=chat_history)
                
                if full_metadata:
                    full_metadata = "\n".join([f'{idx+1}) [{title}][{link}]({date})' for idx, (title, _, date, link) in enumerate(full_metadata)])
                    full_metadata = f'**Ссылки** \n{full_metadata}'
                else:
                    full_metadata = None
                
                errors_to_ignore = ['Error response 401', 'Error response 429', 'error']                
                if any(error.lower() in response.lower() for error in errors_to_ignore):
                    continue
                break

            errors_to_ignore = ['Error response 401', 'Error response 429', 'error']                
            if any(error.lower() in response.lower() for error in errors_to_ignore) or not response:
                raise HTTPException(status_code=400, detail="Ответ от модели пустой или некорректный.")
            
            try:
                user_model = MessageCreate(
                    user_id=data.user_id,
                    human_text=data.text,
                    ai_text=response,
                    full_metadata=full_metadata
                )         
                await uow.message.add_one(user_model.model_dump(), n_tab=0)  
                message = await uow.message.add_one(user_model.model_dump(), n_tab=1)  
                await uow.commit()
                
                return {'role':'ai','ai_text': response, 'full_metadata':full_metadata, 'id':message.id}
            except Exception as err:
                await uow.rollback()
                raise HTTPException(status_code=400, detail="Ошибка при добавлении сообщения в БД. %s" % err)
        

    async def check_token(self, uow: IUnitOfWork, data: Message):
        async with uow:

            token = data.token     
            user_id = data.user_id

            if not token:
                raise HTTPException(status_code=404, detail='Токен не найден.')        

            try:
                self.check_inf(token=token)
                await uow.user.update(where=[User.id==int(user_id)], n_tab=0, values={'token': token})            
                await uow.commit()
                return {
                    "status": "success",                    
                    "message": "Модель подключена и работает корректно.",
                    "token": token
                }
            except Exception as err:
                await uow.user.update(where=[User.id==int(user_id)], n_tab=0, values={'token': None})            
                await uow.commit()
                raise HTTPException(status_code=400, detail="Ошибка при проверке токена. %s" % err)


    async def get_messages(self, uow: IUnitOfWork, data: MessageCreate):
        async with uow:
            checker = await uow.user.get_one(id=data.user_id, n_tab=0)
            if not checker:
                raise HTTPException(status_code=404, detail='Пользователь не найден.')
            try:
                messages = await uow.message.get_all(n_tab=0, user_id=int(data.user_id))
                messages_post = MessageReadAll(**data.model_dump(), posts=messages)                        
            except Exception as err:
                raise HTTPException(status_code=400, detail=f"{err}")            

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

                await uow.message.update(where=[Core.user_id==int(data.user_id), Core.id==data.message_id], n_tab=0, values={'liked': liked})            
                await uow.message.update(where=[Metrics.id==data.message_id, Metrics.user_id==int(data.user_id)], n_tab=1, values={'liked': liked})            
                await uow.commit()

                return {
                    "status": "success",
                    "message":'Оценка пользователя получена.'
                }
            except Exception as err:
                await uow.rollback()
                raise HTTPException(status_code=400, detail=f"{err}")
            
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
                raise HTTPException(status_code=400, detail=f"{err}")
            
    async def get_token(self, uow: IUnitOfWork, data: Message):
        async with uow:
                user = await uow.user.get_one(id=int(data.user_id), n_tab=0)
                token = user.token
                
                if not user:
                    raise HTTPException(status_code=404, detail="Пользователь не найден.")                
                if not token:
                    raise HTTPException(status_code=400, detail="Токена нет!")
                
                return {
                    "status": "success",
                    "message":'Токен в базе есть!',
                    'token':token,
                }


            
    async def add_opinion(self, uow: IUnitOfWork, data: Message):
        async with uow:
            try:
                await uow.message.update(where=[Metrics.id==data.message_id], n_tab=1, values={'opinion': data.opinion})            
                await uow.commit()                
                return {
                        "status": "success",
                        "message":'Спасибо за мнение!',                        
                    }
            except Exception as err:
                await uow.rollback()
                raise HTTPException(status_code=400, detail=f"{err}")