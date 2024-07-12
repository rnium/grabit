import traceback
from fastapi import HTTPException
from typing import List, Tuple
from app.models import Product, User
from app.scraping.product_page_parser import parse_product_page
from app.scraping.website_schema import WebsiteConfig
from app.scraping.websites import get_site_config
from app.config.database import SessionLocal
from app.crud.products import add_product, add_product_data, get_product_from_url
from sqlalchemy.orm import Session
from ..utils.exceptions.site_exceptions import UnSupportedSiteError, NotAProductError
from ..utils.task_manager import TaskManager, Log, LogLevel
from app.config.database import SessionLocal
import asyncio
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
        for i in range(len(urls)):
            url = urls[i]
            log_data = {'total': num_urls, 'nowat': i+1}
            if not manager.is_busy:
                return
            prev_product = db.query(Product).filter(Product.url == url).first()
            if prev_product:
                log_data['message'] = f'Page aready scraped for url: {url}'
                log_data['level'] = LogLevel.warning
            else:
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