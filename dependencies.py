from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from beanie import PydanticObjectId
from datetime import datetime, timedelta
from typing import Optional
from decouple import config
from jose import jwt, JWTError
from models.userModel import User

oath2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


async def get_current_user(token: str = Depends(oath2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config("SECRET_KEY"), algorithms=[config("ALGORITHM")]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await User.find_one(User.email == token_data.email)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config("SECRET_KEY"), algorithm=config("ALGORITHM")
    )
    return encoded_jwt


def generate_url(resource: str, id: PydanticObjectId):
    urlStart = "http://127.0.0.1:8000"
    return f"{urlStart}/{resource}/{id}"
