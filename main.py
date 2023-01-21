from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from routers import usersRouter, gamesRouter
from models.userModel import User
from models.gameModel import Game
from decouple import config

app = FastAPI()

app.include_router(usersRouter.router)
app.include_router(gamesRouter.router)


@app.on_event("startup")
async def app_init():
    """Initialize application services"""
    app.databaseClient = AsyncIOMotorClient(config("MONGO_URI"))
    await init_beanie(database=app.databaseClient.Users, document_models=[User])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
