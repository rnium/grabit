from fastapi import APIRouter, HTTPException, Body, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
from pydantic import HttpUrl, ValidationError
from app.dependencies import DbDependency
from typing import Annotated
from typing import List
from app.scraping.websites import get_site_config
from app.scraping.parse_xml import parse_sitemap_xml
from app.dependencies import UserDependency, BodyUrlDependency
from app.crud import products as prod_crud
from app.schemas import product as prod_schema
from .utils import initiate_and_grab_data, run_url, crawl_urls
from ..utils.task_manager import TaskManager, Log
from ..utils.exceptions.site_exceptions import UnSupportedSiteError
from app.utils.exceptions.logging_exceptions import TaskManagerBusy, TaskManagerOff


import asyncio


router = APIRouter(
    prefix='/product',
    tags=['Product']
)

manager = TaskManager()


async def sample_task():
    get_progress = lambda total, current: (current / total) * 100
    count = 1
    for i in manager.argument:
        await asyncio.sleep(0.2)
        await manager.lognow(Log(i, get_progress(len(manager.argument), count)))
        count += 1
    await manager.finish_task()


@router.get('/all', response_model=List[prod_schema.Product])
def get_all_products(db: DbDependency):
    return prod_crud.get_products(db)


@router.get('/get/{pk}', response_model=prod_schema.Product)
def get_product(db: DbDependency, pk: int):
    return prod_crud.get_product(db, pk)


@router.get('/data')
def product_data(db: DbDependency, q: str = Query()):
    if q.isdigit():
        return prod_crud.get_product_data(db, int(q))
    else:
        try:
            HttpUrl(q)
        except ValidationError:
            raise HTTPException(400, 'Query should be a valid url or an id')
        return prod_crud.get_product_data_from_url(db, q)


@router.post('/testrun')
def test_run_using_product_url(url: Annotated[HttpUrl, Body()]):
    return run_url(str(url))


@router.post('/add', response_model=prod_schema.Product)
def add_product(db: DbDependency, user: UserDependency, url: BodyUrlDependency):
    try:
        prod = initiate_and_grab_data(db, user, str(url))
    except Exception as e:
        raise HTTPException(400, str(e))
    return prod

@router.post('/crawlxml')
async def start_crawl(db: DbDependency, user: UserDependency, url: BodyUrlDependency, bgtask: BackgroundTasks):
    try:
        prod_urls, site_config = parse_sitemap_xml(str(url))
    except Exception as e:
        raise HTTPException(400, str(e))
    try:
        await manager.initiate_task(prod_urls)
    except TaskManagerBusy as e:
        return HTTPException(400, str(e))
    
    bgtask.add_task(crawl_urls, manager, user, prod_urls, site_config)


@router.websocket('/taskstatus')
async def tws(socket: WebSocket):
    await socket.accept()
    manager.add_socket(socket)
    try:
        while True:
            await socket.receive_text()
    except WebSocketDisconnect:
        manager.remove_socket(socket)


