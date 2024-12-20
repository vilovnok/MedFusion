from ..utils.unitofwork import IUnitOfWork
from ..schemas.messages import *
from ..schemas.user import *
from ..models.user import User
from ..models.messages import Message as Core
from fastapi import HTTPException
from agent.src import MedFusionLLM
from agent.src.utils import ModelType


class MessageService:
    async def generate(self, uow: IUnitOfWork, data: Message):
        async with uow:
            checker = await uow.user.get_one(id=int(data.user_id), n_tab=0)

            if not checker:
                raise HTTPException(status_code=404, detail='Пользователь не найден.')
            
            token=checker.token
            agent = MedFusionLLM(model_type=ModelType.MISTRAL, api_key=token)                    
            response = agent.invoke(user_input=data.text, chat_history='')

            if not response:
                raise HTTPException(status_code=400, detail="Ответ от модели пустой или некорректный.")
            try:
                user_model = MessageCreate(
                    user_id=data.user_id,
                    human_text=data.text.replace('\n',''),
                    ai_text=response.replace('\n','')
                )            
                await uow.message.add_one(user_model.model_dump(), n_tab=0)  
                await uow.commit()

                return {'role':'ai','ai_text': response.replace('\n','')}
            except Exception as err:
                await uow.rollback()
                raise HTTPException(status_code=400, detail="Ошибка при добавлении сообщения в БД.")
        
    async def checkToken(self, uow: IUnitOfWork, data: Message):
        async with uow:
            
            token = data.token
            if token=='None':
                raise HTTPException(status_code=404, detail='Токен не найден.')        
                        
            agent = MedFusionLLM(model_type=ModelType.MISTRAL, api_key=token)        
            test_prompt = "проверка"
            try:
                response = agent.healthcheck(test_prompt)
            except Exception as err:
                raise HTTPException(status_code=400, detail="Лимит вашего токена истек.")            
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
            
    async def getMessages(self, uow: IUnitOfWork, data: MessageCreate):
        async with uow:
            checker = await uow.user.get_one(id=int(data.user_id), n_tab=0)
            if not checker:
                raise HTTPException(status_code=404, detail='Пользователь не найден.')
            try:
                messages = await uow.message.get_all(n_tab=0, user_id=int(data.user_id))
                messages_post = MessageReadAll(**data.model_dump(), posts=messages)                              
            except Exception as err:
                raise HTTPException(status_code=400, detail="Лимит вашего токена истек.")            

            if messages_post:
                return {
                    "message": "Модель подключена и работает корректно.",
                    "status": "success",
                    "messages": messages_post
                }
            else:
                raise HTTPException(status_code=400, detail="Лимит вашего токена истек.")
            
    async def Liked(self, uow: IUnitOfWork, data: Message):
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