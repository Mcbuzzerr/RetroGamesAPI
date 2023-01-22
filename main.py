from fastapi import FastAPI, Depends
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from routers import usersRouter, gamesRouter, tradesRouter
from models.userModel import User
from models.gameModel import GameAbstract, OwnedGame
from decouple import config

app = FastAPI()

app.include_router(usersRouter.router)
app.include_router(gamesRouter.router)
app.include_router(tradesRouter.router)


@app.on_event("startup")
async def app_init():
    """Initialize application services"""
    app.databaseClient = AsyncIOMotorClient(config("MONGO_URI"))
    await init_beanie(
        database=app.databaseClient.RetroGames, document_models=[User, GameAbstract]
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
