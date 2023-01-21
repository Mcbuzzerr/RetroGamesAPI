from pydantic import BaseModel
from models.gameModel import GameList


class SearchResults(BaseModel):
    titleResults: GameList
    tagResults: GameList
    platformResults: GameList
    publisherResults: GameList
    total: int
