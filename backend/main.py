from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import HTTPException
from agent.src import MedFusionLLM
from agent.src.utils import ModelType
from backend.schema import  Message, Healhcheck
from fastapi.middleware.cors import CORSMiddleware

# b1u1hPaEICv5ReGjc0ROdnaUqV1ok1Zw xrx8WFJkVRiyqeCJiAiUaeBQttXRjbeh

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
    agent = MedFusionLLM(model_type=ModelType.MISTRAL, api_key=request.api_key)     
    chat_history = " ".join(story for story in list(reversed(request.history)))
    response = agent.invoke(user_input=request.content, chat_history=chat_history)
    
    return {"text": response}


@router.post("/healthcheck")
async def healthcheck(request: Healhcheck):    
    try:
        agent = MedFusionLLM(model_type=ModelType.MISTRAL, api_key=request.api_key)        
        test_prompt = "проверка"
        response = agent.healthcheck(test_prompt)
        
        if response and response.strip():
            return {"status": "success", "message": "Модель подключена и работает корректно."}
        else:
            raise HTTPException(status_code=400, detail="Ответ от модели пустой или некорректный.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Непредвиденная ошибка: {e}")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)