from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from beanie import PydanticObjectId
from models.userModel import User, UserOut, UserRegister, UserUpdate
from models import Tags
from decouple import config
from datetime import timedelta
from dependencies import create_access_token
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


@router.post("/token", status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await User.find_one(User.email == form_data.username)
    if user:
        if bcrypt.checkpw(
            form_data.password.encode("utf-8"), user.password.encode("utf-8")
        ):
            access_token_expires = timedelta(
                minutes=int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))
            )
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise exception
    else:
        raise exception


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


@router.get("", response_model=list[UserOut], status_code=status.HTTP_200_OK)
async def get_users():
    userList: list[UserOut] = []
    async for user in User.find_all():
        userList.append(UserOut(**user.dict()))
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
    "/{userID}", response_model=list[UserOut], status_code=status.HTTP_202_ACCEPTED
)
async def delete_user(userID: PydanticObjectId):
    user = await User.get(userID)
    await user.delete()
    userList: list[UserOut] = []
    async for user in User.find_all():
        userList.append(UserOut(**user.dict()))
    return userList
