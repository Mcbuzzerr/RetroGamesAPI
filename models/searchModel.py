from pydantic import BaseModel
from models.gameModel import GameAbstract


class SearchResults(BaseModel):
    nameResults: list[GameAbstract]
    tagResults: list[GameAbstract]
    platformResults: list[GameAbstract]
    publisherResults: list[GameAbstract]
    total: int
