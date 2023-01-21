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
    "/new",
    response_model=GameAbstract,
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.Games],
)
async def create_game(gameIn: GameAbstract):
    return await GameAbstract(
        id=PydanticObjectId(),
        name=gameIn.name,
        publisher=gameIn.publisher,
        release_date=gameIn.release_date,
        platforms=gameIn.platforms,
        tags=gameIn.tags,
    ).create()


# Read
@router.get("", response_model=list[GameAbstract], status_code=status.HTTP_200_OK)
async def get_games():
    gameList: list[GameAbstract] = []
    async for game in GameAbstract.find_all():
        gameList.append(GameAbstract(**game.dict()))
    return gameList


@router.get("/{game_id}", response_model=GameAbstract, status_code=status.HTTP_200_OK)
async def get_game(game_id: PydanticObjectId):
    return await GameAbstract.get(game_id)


# Update
@router.put(
    "/{game_id}", response_model=GameAbstract, status_code=status.HTTP_202_ACCEPTED
)
async def update_game(game_id: PydanticObjectId, gameIn: GameAbstract):
    game = await GameAbstract.get(game_id)
    game.name = gameIn.name
    game.publisher = gameIn.publisher
    game.release_date = gameIn.release_date
    game.platforms = gameIn.platforms
    game.tags = gameIn.tags
    return await game.save()


# @router.put("", response_model=list[GameAbstract], status_code=status.HTTP_202_ACCEPTED)
# async def update_games():
#     return {"message": "Hello World"}


# Delete
@router.delete(
    "/{game_id}",
    response_model=list[GameAbstract],
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_game(game_id: PydanticObjectId):
    game = await GameAbstract.get(game_id)
    await game.delete()
    gameList: list[GameAbstract] = []
    async for game in GameAbstract.find_all():
        gameList.append(GameAbstract(**game.dict()))
    return gameList


# Search
@router.get("/search/{search_term}", response_model=SearchResults)
async def search_games(search_term: str):
    totalResults = 0
    nameSearch = []
    async for game in GameAbstract.find({"name": {"$regex": search_term}}).limit(25):
        nameSearch.append(game)
        totalResults += 1

    tagSearch = []
    async for game in GameAbstract.find({"tags": {"$regex": search_term}}).limit(25):
        tagSearch.append(game)
        totalResults += 1

    platformSearch = []
    async for game in GameAbstract.find({"platforms": {"$regex": search_term}}).limit(
        25
    ):
        platformSearch.append(game)
        totalResults += 1

    publisherSearch = []
    async for game in GameAbstract.find({"publisher": {"$regex": search_term}}).limit(
        25
    ):
        publisherSearch.append(game)
        totalResults += 1

    results = SearchResults(
        nameResults=nameSearch,
        tagResults=tagSearch,
        platformResults=platformSearch,
        publisherResults=publisherSearch,
        total=totalResults,
    )
    # Searches on multiple fields
    # Title, Tags, Platform, Publisher, Etc.
    return results
