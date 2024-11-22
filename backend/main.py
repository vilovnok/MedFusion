from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

from backend.schema import  Message

# from backend.worker.tasks import generate_task

from agent.src import MedFusionLLM


hf_token='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'
model="microsoft/Phi-3-mini-4k-instruct"

app = FastAPI(title='MedFusion')
agent = MedFusionLLM(model=model, hf_token=hf_token)


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
    
    title = agent.invoke(request.content)
    description = ''
    # task = generate_task.apply_async(args=[request.content])
    # title, description = task.get(timeout=20)

    return {"title": title, "description":description}


app.include_router(router)