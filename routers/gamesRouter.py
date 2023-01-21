from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from models.userModel import User, UserOut
from models.gameModel import GameAbstract, OwnedGame
from models.searchModel import SearchResults
from models import Tags

router = APIRouter(
    prefix="/games",
    responses={
        404: {"description": "Not found"},
        500: {"description": "Server Error"},
    },
    tags=[Tags.Games],
)


# Create
@router.post(
    "",
    response_model=GameAbstract,
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.Games],
)
async def create_game():
    return {"message": "Hello World"}


# Read
@router.get("", response_model=list[GameAbstract], status_code=status.HTTP_200_OK)
async def get_games():
    return {"message": "Hello World"}


@router.get("/{game_id}", response_model=GameAbstract, status_code=status.HTTP_200_OK)
async def get_game(game_id: PydanticObjectId):
    return {"message": "Hello World"}


# Update
@router.put(
    "/{game_id}", response_model=GameAbstract, status_code=status.HTTP_202_ACCEPTED
)
async def update_game(game_id: PydanticObjectId):
    return {"message": "Hello World"}


@router.put("", response_model=list[GameAbstract], status_code=status.HTTP_202_ACCEPTED)
async def update_games():
    return {"message": "Hello World"}


# Delete
@router.delete(
    "/{game_id}",
    response_model=list[GameAbstract],
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_game(game_id: PydanticObjectId):
    return {"message": "Hello World"}


# Search
@router.get("/search/{search_term}", response_model=SearchResults)
async def search_games(search_term: str):
    # Searches on multiple fields
    # Title, Tags, Platform, Publisher, Etc.
    return {"message": "Hello World"}
