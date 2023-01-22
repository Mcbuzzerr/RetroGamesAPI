from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from beanie import PydanticObjectId
from dependencies import oath2_scheme, get_current_user
from models.userModel import User, UserOut, UserAuth
from models.gameModel import GameAbstract, OwnedGame
from models.tradeModel import TradeOffer, TradeStatus
from models import Tags

router = APIRouter(
    prefix="/trade",
    responses={
        404: {"description": "Not found"},
        500: {"description": "Server Error"},
    },
    tags=[Tags.Trades],
)

# REQUIRES AUTH FIRST, THATS HOW WE GET CURRENT USER
# Create
@router.post(
    "/request/{userID}", response_model=TradeOffer, status_code=status.HTTP_201_CREATED
)
async def create_trade(
    userID: PydanticObjectId, tradeIn: TradeOffer, token: str = Depends(oath2_scheme)
):
    offer = await TradeOffer(
        id=PydanticObjectId(),
        status=TradeStatus.pending,
        offererMessage=tradeIn.offererMessage,
        offerer=tradeIn.offerer,
        receiver=userID,
        offererGames=tradeIn.offererGames,
        receiverGames=tradeIn.receiverGames,
    )
    user = await User.get(userID)
    user.tradeHistory.append(offer)
    await user.save()


@router.get("/test")
async def test(user: UserAuth = Depends(get_current_user)):
    return user


# copilot made this, looks interesting. Not what I'm doing right now
# @router.get("/history/{userID}", response_model=list[TradeOffer], status_code=status.HTTP_200_OK)
