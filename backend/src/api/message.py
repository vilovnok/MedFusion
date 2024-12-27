from fastapi import APIRouter
from .dependencies import UOWDep
from ..services.message import MessageService
from ..schemas.messages import Message, Generate, CheckToken, GetToken, Liked, ClearChat, AddOpinion

router = APIRouter(
    prefix='/v1/agent',
    tags=['Message']
)

@router.post('/generate', status_code=201)
async def generate(
    data: Generate,
    uow: UOWDep
):
    res = await MessageService().generate(uow, data)
    return res

@router.post('/check-token', status_code=201)
async def check_token(
    data: CheckToken,
    uow: UOWDep
):
    res = await MessageService().check_token(uow, data)
    return res

@router.post('/get-token', status_code=201)
async def get_token(
    data: GetToken,
    uow: UOWDep
):
    res = await MessageService().get_token(uow, data)
    return res

@router.post('/get-messages', status_code=201)
async def get_messages(
    data: Message,
    uow: UOWDep
):
    res = await MessageService().get_messages(uow, data)
    return res

@router.post('/liked', status_code=201)
async def get_liked(
    data: Liked,
    uow: UOWDep
):
    res = await MessageService().get_liked(uow, data)
    return res

@router.post('/clear-chat', status_code=201)
async def clean_chat(
    data: ClearChat,
    uow: UOWDep
):
    res = await MessageService().clear_chat(uow, data)
    return res

@router.post('/add-opinion', status_code=201)
async def add_opinion(
    data: AddOpinion,
    uow: UOWDep
):
    res = await MessageService().add_opinion(uow, data)
    return res