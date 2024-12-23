from fastapi import FastAPI
from .api.routers import all_routers
from fastapi.middleware.cors import CORSMiddleware

# bE3qXub1g7lA5QehZjV6fSezEdSkpRZH

app = FastAPI(title='RestAPI')
origins = ['http://localhost:80','http://localhost', 'http://127.0.0.1:80']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in all_routers:
    app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)