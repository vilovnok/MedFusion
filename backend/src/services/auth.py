from ..utils.unitofwork import IUnitOfWork
from ..schemas.auth import AuthRegister, AuthLogin
from ..schemas.user import UserCreate
from fastapi.exceptions import HTTPException
from ..models.user import User


class AuthService:
    async def register(self, uow: IUnitOfWork, data: AuthRegister):
        user_model = UserCreate(
            email=data.email,
            password=data.password
        )

        async with uow:
            email_checker = await uow.user.get_one(email=data.email, n_tab=0)
    
            if email_checker:
                await uow.rollback()
                raise HTTPException(status_code=400, detail='Пользователь с таким email уже существует 🙃️️️️️️❌️️️️️️️')
            
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
            if data.password != user.password:
                await uow.rollback()
                raise HTTPException(status_code=400, detail='Неверный password или email 😕🔒')

            return {'user_id': user.id, 'message':f'С возвращением 😁'}