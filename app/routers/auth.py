from fastapi import APIRouter, HTTPException, Body, Depends
from app.dependencies import DbDependency
from app.dependencies import UserDependency
from fastapi.security import OAuth2PasswordRequestForm
from app.crud.users import authenticate_user
from app.dependencies import UserDependency
from app.models import User
from app.schemas.users import UserLogin, UserView
from typing import Annotated
from .utils import get_current_user_from_refresh_token, get_user_tokens
from app.utils.enums import TokenType

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

@router.get('/me', response_model=UserView)
def my_info(user: UserDependency):
    return user


@router.post('/token', response_model=dict)
def get_token(db: DbDependency, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(401, 'Invalid credentials')
    return get_user_tokens(user)


@router.post('/refreshtoken')
def refresh(db: DbDependency, token: Annotated[str, Body()]):
    user = get_current_user_from_refresh_token(db, token)
    return get_user_tokens(user)
    
