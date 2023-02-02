from pydantic import BaseModel, Field
from beanie import PydanticObjectId, Document
from typing import Optional
from enum import Enum
from .gameModel import OwnedGame
from datetime import datetime


class TradeStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class TradeOfferIn(BaseModel):
    offererMessage: str
    offererGames: list[OwnedGame]
    receiverGames: list[OwnedGame]


# https://i.kym-cdn.com/entries/icons/original/000/036/928/cover1.jpg
class TradeOffer(Document, TradeOfferIn):
    id: PydanticObjectId
    status: TradeStatus = TradeStatus.pending
    offerer: str
    receiver: str
    timeOfRequest: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "Trades"
