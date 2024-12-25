from fastapi import FastAPI
from .api.routers import all_routers
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title='RestAPI')
origins = ['http://127.0.0.1:7890','http://0.0.0.0:7890','http://localhost:7890']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in all_routers:
    app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)