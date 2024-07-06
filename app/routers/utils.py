import traceback
from fastapi import HTTPException
from typing import List
from app.models import Product, User
from app.scraping.product_page_parser import parse_product_page
from app.scraping.website_schema import WebsiteConfig
from app.scraping.websites import get_site_config
from app.config.database import SessionLocal
from app.crud.products import add_product, get_product_from_url
from sqlalchemy.orm import Session
from ..utils.exceptions.site_exceptions import UnSupportedSiteError, NotAProductError
from ..utils.task_manager import TaskManager, Log
from app.config.database import SessionLocal


def grab_data(db: Session, product: Product, site_config: WebsiteConfig):
    prod_data = parse_product_page(product.url, site_config)
    product.title = prod_data.title
    product.data = prod_data.model_dump_json()
    product.is_complete = True
    db.commit()


def initiate_and_grab_data(db: Session, user: User, url: str) -> Product:
    try:
        return get_product_from_url(db, url)
    except:
        pass
    site_config = get_site_config(url)
    if not site_config:
        raise UnSupportedSiteError()
    prod = add_product(db, site_config.sitename, user, url)
    grab_data(db, prod, site_config)
    return prod


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


async def crawl_urls(manager: TaskManager, urls: List[str], site_config: WebsiteConfig):
    with SessionLocal() as db:
        count = 0
        for url in urls:
            try:
                data = parse_product_page(url, site_config)
            except Exception as e:
                await manager.lognow(Log(str(e)))
                continue
            await manager.lognow(Log(f'Data parsed for url: {url}'))
            if count == 2:
                break
            count += 1
        await manager.finish_task()
