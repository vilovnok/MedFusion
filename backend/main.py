from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

from backend.schema import  Message
from backend.worker.tasks import generate_task


app = FastAPI(title='MedFusion')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin","Authorization"],
)

router = APIRouter(
    prefix='/v1/agent', 
    tags=['Agent']
)


@router.post("/retrieve-data")
async def generate_text(request: Message):    
    task = generate_task.apply_async(args=[request.content])
    title, description = task.get(timeout=20)

    return {"title": title, "description":description}


app.include_router(router)