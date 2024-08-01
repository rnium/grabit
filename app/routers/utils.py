import traceback
from fastapi import HTTPException, status
from typing import List, Tuple
from app.models import Product, User
from app.config import settings
from app.utils.enums import TokenType
from app.scraping.product_page_parser import parse_product_page
from app.scraping.website_schema import WebsiteConfig
from app.scraping.websites import get_site_config
from app.config.database import SessionLocal
from app.crud.products import add_product, add_product_data, get_product_from_url
from sqlalchemy.orm import Session
from ..utils.exceptions.site_exceptions import UnSupportedSiteError, NotAProductError
from ..utils.task_manager import TaskManager, Log, LogLevel
from app.config.database import SessionLocal
from app.crud.users import get_user_token
from app.crud.products import get_products
import asyncio
import jwt
from jwt.exceptions import InvalidTokenError
from requests import Session


def grab_and_add_data(db: Session, product: Product, site_config: WebsiteConfig):
    prod_data = parse_product_page(product.url, site_config)
    add_product_data(db, product, prod_data)


def initiate_and_grab_data(db: Session, user: User, url: str) -> Tuple[Product, bool]:
    try:
        return get_product_from_url(db, url), False
    except:
        pass
    site_config = get_site_config(url)
    if not site_config:
        raise UnSupportedSiteError()
    prod_data = parse_product_page(url, site_config)
    product = add_product(db, site_config.sitename, user, url)
    add_product_data(db, product, prod_data)
    return product, True


def run_url(url: str, save=False):
    site_config = get_site_config(str(url))
    response = {}
    try:
        if not site_config:
            raise UnSupportedSiteError()
        data = parse_product_page(url, site_config)
        response['status'] = 'successful'
        response['site'] = site_config.sitename
        response['scraped_data'] = data.model_dump()
    except Exception as e:
        response['status'] = 'unsuccessful' 
        response['error'] = f'{type(e).__name__}: {str(e)}'
        response['traceback'] = traceback.format_exc()
    return response


async def crawl_urls(manager: TaskManager, user, urls: List[str], site_config: WebsiteConfig):
    num_urls = len(urls)
    req_session = Session()
    with SessionLocal() as db:
        existing_urls = set([prod.url for prod in get_products(db)])
        crawlable_urls = list(set(urls) - existing_urls)
        num_exclusions = len(urls) - len(crawlable_urls)
        if num_exclusions > 0:
            await manager.add_log(Log(f"Excluding {num_exclusions} urls as these are already crawled.", level=LogLevel.warning)) 
        for i in range(len(crawlable_urls)):
            url = crawlable_urls[i]
            log_data = {'total': num_urls, 'nowat': i+1+num_exclusions}
            if not manager.is_busy:
                return
            try:
                data = parse_product_page(url, site_config, req_session)
                product = add_product(db, site_config.sitename, user, url)
                add_product_data(db, product, data)
                log_data['message'] = f'Data scraped and saved for url: {url}'
            except Exception as e:
                log_data['message'] = f'Error: {str(e)} | url: {url}'
                log_data['level'] = LogLevel.error
            await manager.add_log(Log(**log_data))


async def log_status(manager: TaskManager, log: Log):
    await manager.add_log(log)


def get_current_user_from_refresh_token(db: Session, token: str):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Cannot validate token',
    )
    try:
        payload: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get('username')
        tokentype = payload.get('tokentype')
        if not username or tokentype != TokenType.refresh:
            raise invalid_token_exception
        
    except InvalidTokenError:
        raise invalid_token_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise invalid_token_exception
    return user


def get_user_tokens(user: User):
    user_data = {'username': user.username, 'id': user.id}
    access_token = get_user_token(TokenType.access, user_data)
    refresh_token = get_user_token(TokenType.refresh, user_data)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}