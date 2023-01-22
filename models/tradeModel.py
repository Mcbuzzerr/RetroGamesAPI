from pydantic import BaseModel
from beanie import PydanticObjectId, Document
from typing import Optional
from enum import Enum
from .gameModel import OwnedGame


class TradeStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


# https://i.kym-cdn.com/entries/icons/original/000/036/928/cover1.jpg
class TradeOffer(BaseModel):
    id: PydanticObjectId = PydanticObjectId()
    status: TradeStatus = TradeStatus.pending
    offererMessage: str
    offerer: PydanticObjectId
    receiver: PydanticObjectId
    offererGames: list[OwnedGame]
    receiverGames: list[OwnedGame]
