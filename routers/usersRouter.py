from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from models.userModel import User, UserOut, UserRegister, UserList, UserUpdate
from models.gameModel import Game, GameOut, GameList
from models import Tags
from decouple import config
import bcrypt

router = APIRouter(
    prefix="/users",
    responses={
        404: {"description": "Not found"},
        500: {"description": "Server Error"},
        403: {"description": "Forbidden"},
    },
    tags=[Tags.Users],
)

# Create
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(newUser: UserRegister):
    user = await User(
        id=PydanticObjectId(),
        username=newUser.username,
        email=newUser.email,
        password=bcrypt.hashpw(
            newUser.password.encode("utf-8"),
            bcrypt.gensalt(),
        ),
        street_address=newUser.street_address,
    ).create()
    # TODO: Hash password
    return UserOut(**user.dict())


# Read
@router.get("/{userID}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_users(userID: PydanticObjectId):
    user = await User.get(userID)
    return UserOut(**user.dict())


@router.get("", response_model=UserList, status_code=status.HTTP_200_OK)
async def get_users():
    userList = UserList()
    async for user in User.find_all():
        userList.users.append(UserOut(**user.dict()))
    return userList


# Update
@router.patch("/{userID}", response_model=UserOut, status_code=status.HTTP_202_ACCEPTED)
async def update_user(userID: PydanticObjectId, userIn: UserUpdate):
    user = await User.get(userID)
    print(user)
    user.username = userIn.username
    user.first_name = userIn.first_name
    user.last_name = userIn.last_name
    user.password = userIn.password
    user.date_of_birth = userIn.date_of_birth
    user.street_address = userIn.street_address
    user.games = userIn.games
    print(user)
    await user.save()
    return UserOut(**user.dict())


# Delete
@router.delete(
    "/{userID}", response_model=UserList, status_code=status.HTTP_202_ACCEPTED
)
async def delete_user(userID: PydanticObjectId):
    user = await User.get(userID)
    await user.delete()
    userList = UserList()
    async for user in User.find_all():
        userList.users.append(UserOut(**user.dict()))
    return userList
