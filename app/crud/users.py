from app.models import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
import jwt
from datetime import timedelta, datetime, timezone
from app.config import settings
from app.utils.enums import TokenType

context = CryptContext(schemes=['bcrypt'], deprecated="auto")


def create_user(db: Session, user_data: dict):
    hashed_password = context.hash(user_data.get('password'))
    user_model = User(
        username=user_data.get('username'),
        name=user_data.get('name'),
        hashed_password=hashed_password
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_data


def authenticate_user(db: Session, username, password):
    user = db.query(User).filter(User.username==username).first()
    if user:
        if context.verify(password, user.hashed_password):
            return user
    return False


def get_user_token(tokentype: TokenType, data: dict, expiration_delta: timedelta | None = None):
    payload = data.copy()
    if not expiration_delta:
        expiration_delta = timedelta(
            minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES if tokentype == TokenType.access else settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    expires = datetime.now(timezone.utc) + expiration_delta
    payload.update({'exp': expires, 'tokentype': tokentype.value})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token
