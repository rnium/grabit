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
from ..utils.task_manager import TaskManager, Log
from app.config.database import SessionLocal
import asyncio


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
    prod = add_product(db, site_config.sitename, user, url)
    grab_and_add_data(db, prod, site_config)
    return prod, True


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
    with SessionLocal() as db:
        count = 0
        for url in urls:
            prev_product = db.query(Product).filter(Product.url == url).first()
            if prev_product:
                await manager.add_log(Log(f'Page aready scraped for url: {url}'))
                continue
            try:
                data = parse_product_page(url, site_config)
                product = add_product(db, site_config.sitename, user, url)
                add_product_data(db, product, data)
            except Exception as e:
                await manager.add_log(Log(str(e)))
                continue
            await manager.add_log(Log(f'Data scraped and saved for url: {url}'))
            if count == 4:
                break
            count += 1  
        await manager.finish_task()

async def log_status(manager: TaskManager, log: Log):
    await manager.add_log(log)