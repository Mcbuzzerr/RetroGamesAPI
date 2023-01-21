import datetime
from pydantic import BaseModel
from beanie import PydanticObjectId, Document
from typing import Optional
from .gameModel import GameList, Tags


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
    games: Optional[GameList]

    class Config:
        schema_extra = {
            "example": {
                "username": "XxX_The_Gamer_XxX",
                "email": "GamerGod@gmail.com",
                "games": [
                    {
                        "name": "Crash Bandicoot",
                        "publisher": "Naughty Dog",
                        "release_date": "1996-10-0",
                        "platforms": ["Playstation", "Playstation 2", "Playstation 3"],
                        "owner_history": ["XxX_The_Gamer_XxX"],
                        "tags": [
                            Tags.Platformer,
                        ],
                    },
                ],
            }
        }


class UserUpdate(BaseModel):

    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
    date_of_birth: Optional[datetime.date]
    street_address: Optional[Address]
    games: Optional[GameList]


class User(Document, UserOut):
    """User DB representation"""

    id: PydanticObjectId = PydanticObjectId()
    password: str
    first_name: str = "John"
    last_name: str = "Doe"
    date_of_birth: Optional[datetime.date]
    street_address: Address

    class Settings:
        name = "Users"
        bson_encoders = {
            datetime.date: lambda v: v.isoformat(),  # Copilot gave me this and idk what its doing, ask a python expert
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


class UserList(BaseModel):
    users: list[UserOut] = []
