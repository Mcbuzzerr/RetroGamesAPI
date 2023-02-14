from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from beanie import PydanticObjectId
from models.userModel import User, UserOut, UserRegister, UserUpdate, UserNewPassword
from models.gameModel import OwnedGame, GameAbstract
from models import Tags
from decouple import config
from datetime import timedelta
from dependencies import create_access_token, get_current_user, generate_url
from util.kafkaUtil import producer
import bcrypt

router = APIRouter(
    prefix="/users",
    responses={
        404: {"description": "Not found"},
        500: {"description": "Server Error"},
        403: {"description": "Forbidden"},
    },
)


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    summary="Login Endpoint",
    description="This endpoint is used to login, it provides a JWT token that can be used to access the API",
    tags=[Tags.Auth],
)
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


@router.get(
    "/test",
    response_model=User,
    status_code=status.HTTP_200_OK,
    tags=[Tags.Test],
    summary="Test endpoint",
    description="This endpoint is used to test the authentication, returns the current full user object",
)
async def test(user: User = Depends(get_current_user)):
    return user


# Create
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register Endpoint",
    description="This endpoint is used to register a new user",
    tags=[Tags.Auth],
)
async def create_user(newUser: UserRegister):
    producerInstance = producer({"bootstrap.servers": "retro-games-kafka-broker:29092"})
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
    print("LORG")
    producerInstance.produce("user", user.dict().__str__().encode("utf-8"))
    return UserOut(**user.dict())


@router.get(
    "",
    response_model=list[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    description="This endpoint is used to get all users",
    tags=[Tags.Users],
)
async def get_users():
    userList: list[UserOut] = []
    async for user in User.find_all():
        userList.append(UserOut(**user.dict()))
    return userList


@router.patch(
    "/change-password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Change password",
    description="This endpoint is used to change the password of the current user",
    tags=[Tags.Auth],
)
async def change_password(
    body: UserNewPassword, currentUser: User = Depends(get_current_user)
):
    if bcrypt.checkpw(
        body.oldPassword.encode("utf-8"), currentUser.password.encode("utf-8")
    ):
        currentUser.password = bcrypt.hashpw(
            body.newPassword.encode("utf-8"), bcrypt.gensalt()
        )
        await currentUser.save()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )


# LIBRARY FUNCTIONS
@router.post(
    "/library",
    response_model=list[OwnedGame],
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.Library],
    summary="Add game to library",
    description="This endpoint is used to add a game to the current user's library",
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
    summary="Get library",
    description="This endpoint is used to get the current user's library",
)
async def get_library(currentUser: User = Depends(get_current_user)):
    return currentUser.games


@router.delete(
    "/library/{gameID}",
    tags=[Tags.Library],
    status_code=status.HTTP_202_ACCEPTED,
    response_model=list[OwnedGame],
    summary="Delete game from library",
    description="This endpoint is used to delete a game from the current user's library",
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
    summary="Update game in library",
    description="This endpoint is used to update a game in the current user's library (the only editible data is the condition)",
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
@router.get(
    "/{userID}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get user",
    description="This endpoint is used to get a user by ID",
    tags=[Tags.Users],
)
async def get_users(userID: PydanticObjectId):
    user = await User.get(userID)
    return UserOut(**user.dict())


# Update
@router.patch(
    "/{userID}",
    response_model=UserOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update user",
    description="This endpoint is used to update a user by ID. The only editable data is the username, first name, last name, and date of birth. The password must be changed using the change-password endpoint",
    tags=[Tags.Users],
)
async def update_user(userID: PydanticObjectId, userIn: UserUpdate):
    user = await User.get(userID)

    if not bcrypt.checkpw(
        userIn.password.encode("utf-8"), user.password.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    if userIn.username is not None:
        user.username = userIn.username
    if userIn.first_name is not None:
        user.first_name = userIn.first_name
    if userIn.last_name is not None:
        user.last_name = userIn.last_name
    if userIn.date_of_birth is not None:
        user.date_of_birth = userIn.date_of_birth
    if userIn.street_address is not None:
        user.street_address = userIn.street_address
    if userIn.games is not None:
        user.games = userIn.games
    await user.save()
    return UserOut(**user.dict())


# Delete
@router.delete(
    "/{userID}",
    response_model=list[UserOut],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Delete user",
    description="This endpoint is used to delete a user by ID",
    tags=[Tags.Users],
)
async def delete_user(userID: PydanticObjectId):
    user = await User.get(userID)
    await user.delete()
    userList: list[UserOut] = []
    async for user in User.find_all():
        userList.append(UserOut(**user.dict()))
    return userList
