import datetime
from pydantic import BaseModel
from beanie import PydanticObjectId, Document
from typing import Optional
from .gameModel import Tags, OwnedGame
from .tradeModel import TradeOffer

# I need hypermedia functionality
# idea, users have a different form of the game class
# this one stores only the info unique to their copy, and a link to the abstract version of that game
# Games collection stores the abstract version of the game
# Users gamesList stores the link to the abstract version of the game and the condition


class Address(BaseModel):
    street: str
    city: str
    state: str
    zipcode: str
    country: str


class UserOut(BaseModel):
    """User fields returned to the client"""

    id: PydanticObjectId
    username: str
    email: str
    games: list[OwnedGame] = []
    tradeHistory: list[TradeOffer] = []
    # LIST OF TRADE OFFERS GOES ON ONE OF THE USER MODELS, both parties included

    class Config:
        schema_extra = {
            "example": {
                "username": "XxX_The_Gamer_XxX",
                "email": "GamerGod@gmail.com",
                "games": [],
            }
        }


class UserUpdate(BaseModel):

    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
    date_of_birth: Optional[datetime.date]
    street_address: Optional[Address]
    games: Optional[list[OwnedGame]]


class User(Document, UserOut):
    """User DB representation"""

    id: PydanticObjectId = PydanticObjectId()
    password: str
    first_name: str = "John"
    last_name: str = "Doe"
    date_of_birth: Optional[datetime.date]
    street_address: Address
    # disabled: bool = False # This would be instead of deleting the user

    class Settings:
        name = "Users"
        bson_encoders = {
            datetime.date: lambda v: v.isoformat(),
        }


class UserRegister(BaseModel):
    """User fields required to register"""

    username: str
    email: str
    password: str
    street_address: Address

    class Config:
        schema_extra = {
            "example": {
                "username": "XxX_The_Gamer_XxX",
                "email": "GodGamer@gmail.com",
                "password": "l33tH4x0r",
                "street_address": {
                    "street": "1234 Main",
                    "city": "Anytown",
                    "state": "CA",
                    "zipcode": "12345",
                    "country": "USA",
                },
            }
        }


# I don't think I'm actually using this
class UserAuth(BaseModel):
    """User fields required to authenticate"""

    token: str
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "GodGamer@gmail.com",
                "password": "l33tH4x0r",
            }
        }
