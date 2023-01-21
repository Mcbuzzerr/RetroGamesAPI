import datetime
from pydantic import BaseModel
from beanie import PydanticObjectId, Document
from enum import Enum


class Tags(Enum):
    """Game Tags"""

    Action = "Action"
    Adventure = "Adventure"
    Puzzle = "Puzzle"
    Strategy = "Strategy"
    RPG = "RPG"
    FPS = "FPS"
    Survival = "Survival"
    Horror = "Horror"
    Platformer = "Platformer"
    Racing = "Racing"
    Sports = "Sports"
    MMO = "MMO"
    MOBA = "MOBA"
    RTS = "RTS"
    Card = "Card"
    Fighting = "Fighting"
    Sandbox = "Sandbox"
    Open_World = "Open World"
    Turn_based = "Turn-based"
    Turn_based_Strategy = "Turn-based Strategy"
    Turn_based_Tactics = "Turn-based Tactics"
    Roguelike = "Roguelike"
    Roguelite = "Roguelite"
    Metroidvania = "Metroidvania"
    Visual_Novel = "Visual Novel"
    Point_and_Click = "Point and Click"
    Text_Adventure = "Text Adventure"
    Dating_Sim = "Dating Sim"
    Action_RPG = "Action RPG"
    Tactical_RPG = "Tactical RPG"
    Turn_based_RPG = "Turn-based RPG"
    JRPG = "JRPG"
    ARPG = "ARPG"
    MMORPG = "MMORPG"
    MOBA_RPG = "MOBA RPG"
    Roguelike_RPG = "Roguelike RPG"
    Roguelite_RPG = "Roguelite RPG"
    Action_Adventure = "Action Adventure"
    Survival_Adventure = "Survival Adventure"
    Survival_Horror = "Survival Horror"
    Stealth = "Stealth"
    Action_Platformer = "Action Platformer"
    Puzzle_Platformer = "Puzzle Platformer"
    Racing_Simulator = "Racing Simulator"
    Sports_Simulator = "Sports Simulator"
    Battle_Royale = "Battle Royale"
    Survival_Crafting = "Survival Crafting"
    Survival_Crafting_Sandbox = "Survival Crafting Sandbox"
    Survival_Crafting_Open_World = "Survival Crafting Open World"
    Survival_Crafting_Sandbox_Open_World = "Survival Crafting Sandbox Open World"
    Survival_Crafting_Sandbox_Open_World_Turn_based = (
        "Survival Crafting Sandbox Open World Turn-based"
    )


class GameAbstract(Document):
    """Game DB representation"""

    id: PydanticObjectId = PydanticObjectId()
    name: str
    publisher: str
    release_date: datetime.date
    platforms: list[str]
    tags: list[Tags]
    usersWithGame: list[str] = []  # list of users who own this game

    class Settings:
        name = "Games"
        bson_encoders = {
            datetime.date: lambda v: v.isoformat(),  # Copilot gave me this and idk what its doing, ask a python expert
        }


class OwnedGame(BaseModel):
    game: str  # link to the abstract version of the game
    condition: str
    owner: str  # link to the user who owns the game
    ownerHistory: list[str]  # list of users who have owned the game


# I need hypermedia functionality
# idea, users have a different form of the game class
# this one stores only the info unique to their copy, and a link to the abstract version of that game
# Games collection stores the abstract version of the game
# Users gamesList stores the link to the abstract version of the game and the condition
