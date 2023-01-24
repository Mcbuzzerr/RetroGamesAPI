from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordBearer
from beanie import PydanticObjectId
from dependencies import oath2_scheme, get_current_user, generate_url
from models.userModel import User, UserOut
from models.gameModel import GameAbstract, OwnedGame
from models.tradeModel import TradeOffer, TradeStatus, TradeOfferIn
from models import Tags

router = APIRouter(
    prefix="/trades",
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
    userID: PydanticObjectId,
    tradeIn: TradeOfferIn = Body(
        example={
            "offererMessage": "I want to trade these games for your games",
            "offererGames": [
                {
                    "id": PydanticObjectId(),
                    "game": PydanticObjectId(),
                    "name": "Super Mario Bros",
                    "condition": "Good",
                }
            ],
            "receiverGames": [
                {
                    "id": PydanticObjectId(),
                    "game": PydanticObjectId(),
                    "name": "Sonic the Hedgehog",
                    "condition": "Good",
                }
            ],
        }
    ),
    currentUser: User = Depends(get_current_user),
):
    user = await User.get(userID)

    foundGame: bool = False
    formattedOffererGames: list[OwnedGame] = []
    for game in tradeIn.offererGames:
        for OwnedGameIn in currentUser.games:
            if OwnedGameIn.id == game.id:
                formattedOffererGames.append(OwnedGameIn)
                foundGame = True

    if not foundGame:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't own the game you're trying to trade",
        )

    foundGame: bool = False
    formattedReceiverGames: list[OwnedGame] = []
    for game in tradeIn.receiverGames:
        for OwnedGameIn in user.games:
            if OwnedGameIn.id == game.id:
                formattedReceiverGames.append(OwnedGameIn)
                foundGame = True

    if not foundGame:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user you're trying to trade with doesn't own that game",
        )

    offer = await TradeOffer(
        id=PydanticObjectId(),
        status=TradeStatus.pending,
        offerer=generate_url("users", currentUser.id),
        receiver=generate_url("users", user.id),
        offererMessage=tradeIn.offererMessage,
        offererGames=formattedOffererGames,
        receiverGames=formattedReceiverGames,
    ).create()
    user.tradeHistory.append(generate_url("trades", offer.id))
    currentUser.tradeHistory.append(generate_url("trades", offer.id))
    await currentUser.save()
    await user.save()
    return offer


@router.get(
    "/myTrades", response_model=list[TradeOffer], status_code=status.HTTP_200_OK
)
async def get_user_trades(user: User = Depends(get_current_user)):
    trades: list[TradeOffer] = []
    for link in user.tradeHistory:
        id = link.split("/")[-1]
        trades.append(await TradeOffer.get(id))
    return trades


@router.get(
    "/myTrades/pending", response_model=list[TradeOffer], status_code=status.HTTP_200_OK
)
async def get_user_pending_trades(user: User = Depends(get_current_user)):
    trades: list[TradeOffer] = []
    for link in user.tradeHistory:
        id = link.split("/")[-1]
        trade = await TradeOffer.get(id)
        if trade.status == TradeStatus.pending:
            trades.append(trade)
    return trades


@router.get(
    "/myTrades/accepted",
    response_model=list[TradeOffer],
    status_code=status.HTTP_200_OK,
)
async def get_user_accepted_trades(user: User = Depends(get_current_user)):
    trades: list[TradeOffer] = []
    for link in user.tradeHistory:
        id = link.split("/")[-1]
        trade = await TradeOffer.get(id)
        if trade.status == TradeStatus.accepted:
            trades.append(trade)
    return trades


@router.get(
    "/myTrades/declined",
    response_model=list[TradeOffer],
    status_code=status.HTTP_200_OK,
)
async def get_user_declined_trades(user: User = Depends(get_current_user)):
    trades: list[TradeOffer] = []
    for link in user.tradeHistory:
        id = link.split("/")[-1]
        trade = await TradeOffer.get(id)
        if trade.status == TradeStatus.declined:
            trades.append(trade)
    return trades


@router.get("/test")
async def test(user: User = Depends(get_current_user)):
    return user


@router.get("/{tradeID}", response_model=TradeOffer, status_code=status.HTTP_200_OK)
async def get_trade(tradeID: PydanticObjectId):
    return await TradeOffer.get(tradeID)


@router.post(
    "/accept/{tradeID}", response_model=TradeOffer, status_code=status.HTTP_200_OK
)
async def accept_trade(
    tradeID: PydanticObjectId, user: User = Depends(get_current_user)
):
    trade = await TradeOffer.get(tradeID)
    if trade.status != TradeStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This trade is not pending",
        )
    if trade.receiver != generate_url("users", user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the receiver of this trade",
        )
    offerer = await User.get(trade.offerer.split("/")[-1])
    trade.status = TradeStatus.accepted
    for game in trade.offererGames:
        user.games.append(game)
        for userGame in offerer.games:
            if userGame.id == game.id:
                offerer.games.remove(userGame)
    for game in trade.receiverGames:
        offerer.games.append(game)
        for userGame in user.games:
            if userGame.id == game.id:
                user.games.remove(userGame)
    await user.save()
    await offerer.save()
    await trade.save()
    return trade


@router.post(
    "/decline/{tradeID}", response_model=TradeOffer, status_code=status.HTTP_200_OK
)
async def decline_trade(
    tradeID: PydanticObjectId, user: User = Depends(get_current_user)
):
    trade = await TradeOffer.get(tradeID)
    if trade.status != TradeStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This trade is not pending",
        )
    if trade.receiver != generate_url("users", user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the receiver of this trade",
        )
    trade.status = TradeStatus.declined
    await trade.save()
    return trade
