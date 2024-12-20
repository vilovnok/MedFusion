from ..utils.unitofwork import IUnitOfWork
from ..schemas.auth import AuthRegister, AuthLogin
from ..schemas.user import UserCreate
from ..schemas.token import TokenRefresh, TokenData
from ..auth.auth import bcrypt_context, create_access_token, decode_token
from fastapi.exceptions import HTTPException
from ..models.user import User
from datetime import timedelta
from ..config import SECRET, REFRESH_SECRET, ALGORITHM

class AuthService:
    async def register(self, uow: IUnitOfWork, data: AuthRegister):
        user_model = UserCreate(
            username=data.username,
            email=data.email,
            hashed_password=bcrypt_context.hash(data.password),
            token='nan'
        )

        async with uow:
            email_checker = await uow.user.get_one(email=data.email, n_tab=0)
            username_checker = await uow.user.get_one(username=data.username, n_tab=0)
            
    
            if email_checker:
                await uow.rollback()
                raise HTTPException(status_code=400, detail='Пользователь с таким email уже существует 🙃️️️️️️❌️️️️️️️')
            
            if username_checker:
                await uow.rollback()
                raise HTTPException(status_code=400, detail='Пользователь с таким username уже существует 😅️️️️️️❌️️️️️️️')
            
            user = await uow.user.add_one(user_model.model_dump(), n_tab=0)           
            
            if not user:                
                await uow.rollback()
                raise HTTPException(status_code=400)
            await uow.commit()
            
            res = {
                'user_id': f'{user.id}', 
                'message':"Вы зарегистрированы 🙂️️🔥️️️️️️✅️️️️️️️"
                }
            
            return res
        

    async def login(self, uow: IUnitOfWork, data: AuthLogin):
        async with uow:
            user: User = await uow.user.get_one(email= data.email, full_model=True,n_tab=0)
            
            if not user:            
                await uow.rollback()
                raise HTTPException(status_code=400, detail='Неверный password или email 😕🔒')
            if not bcrypt_context.verify(data.password, user.hashed_password):
                await uow.rollback()
                raise HTTPException(status_code=400, detail='Неверный password или email 😕🔒')

            return {'user_id': user.id, 'message':f'С возвращением, {user.username} 👋😁'}