from .config.database import SessionLocal
from typing import Annotated
from pydantic import HttpUrl
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from .config import settings
from app.models import User
from app.utils.enums import TokenType
import jwt
from jwt.exceptions import InvalidTokenError


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbDependency = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer('auth/token')

def get_current_user(db: DbDependency, token: Annotated[str, Depends(oauth2_scheme)]):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Cannot validate token',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get('username')
        tokentype = payload.get('tokentype')
        if not username or tokentype != TokenType.access:
            raise invalid_token_exception
        
    except InvalidTokenError:
        raise invalid_token_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise invalid_token_exception
    return user

UserDependency = Annotated[User, Depends(get_current_user)]

BodyUrlDependency = Annotated[HttpUrl, Body()]