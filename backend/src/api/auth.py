from fastapi import APIRouter
from .dependencies import UOWDep
from ..services.auth import AuthService
from ..schemas.auth import AuthRegister, AuthLogin
from ..schemas.token import TokenCreate, TokenRefresh

router = APIRouter(
    prefix='/v1/auth',
    tags=['Auth']
)

@router.post('/register', status_code=201)
async def register(
    data: AuthRegister,
    uow: UOWDep
):
    res = await AuthService().register(uow, data)
    return res

@router.post('/login', status_code=201)
async def login(
    data: AuthLogin,
    uow: UOWDep
):
    res = await AuthService().login(uow, data)
    return res
