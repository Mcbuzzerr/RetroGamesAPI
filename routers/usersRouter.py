from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from beanie import PydanticObjectId
from models.userModel import User, UserOut, UserRegister, UserUpdate
from models.gameModel import OwnedGame, GameAbstract
from models import Tags
from decouple import config
from datetime import timedelta
from dependencies import create_access_token, get_current_user, generate_url
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


@router.get("", response_model=list[UserOut], status_code=status.HTTP_200_OK)
async def get_users():
    userList: list[UserOut] = []
    async for user in User.find_all():
        userList.append(UserOut(**user.dict()))
    return userList


# LIBRARY FUNCTIONS
@router.post(
    "/library",
    response_model=list[OwnedGame],
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.Library],
)
async def add_game(
    gameIn: OwnedGame = Body(
        example={"game": PydanticObjectId(), "name": "Game Name", "condition": "Good"}
    ),
    currentUser: User = Depends(get_current_user),
):
    gameAbstract = await GameAbstract.get(gameIn.game)
    if gameAbstract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username or password",
        )
    newGameObject = OwnedGame(
        id=PydanticObjectId(),
        game=generate_url("games", gameIn.game),
        name=gameAbstract.name,
        condition=gameIn.condition,
        owner=generate_url("users", currentUser.id),
        ownerHistory=[generate_url("users", currentUser.id)],
    )
    currentUser.games.append(newGameObject)
    await currentUser.save()
    return currentUser.games


@router.get(
    "/library",
    response_model=list[OwnedGame],
    status_code=status.HTTP_200_OK,
    tags=[Tags.Library],
)
async def get_library(currentUser: User = Depends(get_current_user)):
    return currentUser.games


@router.delete(
    "/library/{gameID}",
    tags=[Tags.Library],
    status_code=status.HTTP_202_ACCEPTED,
    response_model=list[OwnedGame],
)
async def delete_game(
    gameID: PydanticObjectId, currentUser: User = Depends(get_current_user)
):
    gameAbstract = await GameAbstract.get(gameID)
    for game in currentUser.games:
        if game.id == gameID:
            currentUser.games.remove(game)
            await currentUser.save()
            return currentUser.games
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Game not found",
    )


@router.put(
    "/library/{gameID}",
    tags=[Tags.Library],
    status_code=status.HTTP_202_ACCEPTED,
    response_model=OwnedGame,
)
async def update_game(
    gameID: PydanticObjectId,
    gameIn: OwnedGame = Body(example={"condition": "Good"}),
    currentUser: User = Depends(get_current_user),
):
    for game in currentUser.games:
        if game.id == gameID:
            game.condition = gameIn.condition
            return await currentUser.save()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Game not found",
    )


# ------------------------- USER ROUTES ------------------------- #

# Read
@router.get("/{userID}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_users(userID: PydanticObjectId):
    user = await User.get(userID)
    return UserOut(**user.dict())


# Update
@router.patch("/{userID}", response_model=UserOut, status_code=status.HTTP_202_ACCEPTED)
async def update_user(userID: PydanticObjectId, userIn: UserUpdate):
    user = await User.get(userID)
    print(user)
    if userIn.username is not None:
        user.username = userIn.username
    if userIn.first_name is not None:
        user.first_name = userIn.first_name
    if userIn.last_name is not None:
        user.last_name = userIn.last_name
    if userIn.password is not None:
        user.password = bcrypt.hashpw(userIn.password, bcrypt.gensalt())
    if userIn.date_of_birth is not None:
        user.date_of_birth = userIn.date_of_birth
    if userIn.street_address is not None:
        user.street_address = userIn.street_address
    if userIn.games is not None:
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
