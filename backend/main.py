from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from fastapi import HTTPException

from backend.schema import  Message, Healhcheck

# from backend.worker.tasks import generate_task

from agent.src import MedFusionLLM


hf_token = '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'
model_name = "mistral-large-latest"
# api_key = 'b1u1hPaEICv5ReGjc0ROdnaUqV1ok1Zw'

app = FastAPI(title='MedFusion')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:4200'],
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
    agent = MedFusionLLM(model_name=model_name, hf_token=hf_token, api_key=request.api_key)     
    text = agent.invoke(content=request.content)

    return {"text": text}


@router.post("/healthcheck")
async def healthcheck(request: Healhcheck):    
    try:
        agent = MedFusionLLM(model_name=model_name, api_key=request.api_key)        
        test_prompt = "Проверка подключения к модели."
        response = agent.invoke(test_prompt)
        
        if response and response.strip():
            return {"status": "success", "message": "Модель подключена и работает корректно."}
        else:
            raise HTTPException(status_code=400, detail="Ответ от модели пустой или некорректный.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Непредвиденная ошибка: {e}")

app.include_router(router)