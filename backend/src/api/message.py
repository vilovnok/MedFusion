from fastapi import APIRouter
from .dependencies import UOWDep
from ..services.message import MessageService
from ..schemas.messages import Message

router = APIRouter(
    prefix='/v1/agent',
    tags=['Message']
)

@router.post('/generate', status_code=201)
async def generate(
    data: Message,
    uow: UOWDep
):
    res = await MessageService().generate(uow, data)
    return res

@router.post('/check-token', status_code=201)
async def check_token(
    data: Message,
    uow: UOWDep
):
    res = await MessageService().checkToken(uow, data)
    return res


@router.post('/get-messages', status_code=201)
async def getmessages(
    data: Message,
    uow: UOWDep
):
    res = await MessageService().getMessages(uow, data)
    return res