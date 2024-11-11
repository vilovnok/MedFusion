from backend.schema import  Message

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
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


@router.post("/generate")
async def generate_text(request: Message):    
    task = generate_task.apply_async(args=[request.content])
    result = task.get(timeout=2)

    return {"result": result, "status": 'success'}


# @app.post("/v1/agent/number-test")
# async def number_text():    
#     task = number_test_task.delay('Нормально, хорошо, отлично')
#     return {"task_id": task.id, "status": 'success'}


# @app.post("/v1/agent/number123-test")
# async def number_text():    
#     task = number_topic_task.delay()
#     return {"task_id": task.id, "status": 'success'}


# @app.get("/v1/agent/result/{task_id}")
# async def task_result(task_id: str):    
    # return get_task_info(task_id)


app.include_router(router)