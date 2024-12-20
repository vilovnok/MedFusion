from fastapi import FastAPI
from .api.routers import all_routers
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title='RestAPI')

origins = ["http://localhost",
           "http://0.0.0.0",
           "http://localhost:80",
           "http://localhost:4200",
           "http://0.0.0.0:80",           
           "http://10.220.16.103",
           "http://10.220.16.103:80"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin","Authorization"],
)

for router in all_routers:
    app.include_router(router)

# @app.on_event("startup")
# async def startup_event():
#     redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)