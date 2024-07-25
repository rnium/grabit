from fastapi import APIRouter, HTTPException, Body, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import HttpUrl, ValidationError
from app.dependencies import DbDependency
from typing import Annotated
from typing import List
import httpx
from io import BytesIO
from app.scraping.parse_xml import parse_sitemap_xml
from app.dependencies import UserDependency, UrlDependency
from app.crud import products as prod_crud
from app.schemas import product as prod_schema
from .utils import initiate_and_grab_data, run_url, crawl_urls, log_status
from ..utils.task_manager import TaskManager, Log
from ..utils.exceptions.site_exceptions import UnSupportedSiteError
from app.utils.exceptions.logging_exceptions import TaskManagerBusy, TaskManagerOff


import asyncio


router = APIRouter(
    prefix='/product',
    tags=['Product']
)

manager = TaskManager()


@router.get('/all', response_model=List[prod_schema.Product])
def get_all_products(db: DbDependency):
    return prod_crud.get_products(db)


@router.get('/search', response_model=List[prod_schema.Product])
def search_product(db: DbDependency, query: Annotated[str, Query()]):
    return prod_crud.search_product(db, query)


@router.get('/get/{pk}', response_model=prod_schema.Product)
def get_product(db: DbDependency, pk: int):
    return prod_crud.get_product(db, pk)
    

@router.delete('/delete/{pk}')
def delete_product(db: DbDependency, pk: int, user: UserDependency):
    prod_crud.delete_product(db, pk)
    return "Deleted"


@router.get('/data')
def product_data(db: DbDependency, query: Annotated[str, Query()]):
    if query.isdigit():
        return prod_crud.get_product_data(db, int(query))
    else:
        try:
            HttpUrl(query)
        except ValidationError:
            raise HTTPException(400, 'Query should be a valid url or an id')
        return prod_crud.get_product_data_from_url(db, query)


@router.get('/getimage')
async def get_image_from_url(url: Annotated[HttpUrl, Query()]):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(str(url))
            res.raise_for_status()
            return StreamingResponse(BytesIO(res.content), media_type=res.headers.get('content-type'))
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            res.status_code,
            f'Error for url: {url}'
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"An error occurred while requesting {url}: {e}")


@router.post('/testrun')
def test_run_using_product_url(url: UrlDependency):
    return run_url(str(url))


@router.post('/add', response_model=prod_schema.Product)
def add_product(db: DbDependency, user: UserDependency, url: UrlDependency, bgtask: BackgroundTasks):
    try:
        prod, created = initiate_and_grab_data(db, user, str(url))
    except Exception as e:
        raise HTTPException(400, str(e))
    if created:
        bgtask.add_task(log_status, manager, Log(f"Product added for url: {url}"))
    else:
        raise HTTPException(400, 'Product already added to the database. id: {}'.format(prod.id))
    return prod


@router.post('/crawlxml')
async def start_crawl(db: DbDependency, user: UserDependency, url: UrlDependency, bgtask: BackgroundTasks):
    try:
        prod_urls, site_config = parse_sitemap_xml(str(url))
    except Exception as e:
        raise HTTPException(400, str(e))
    if manager.is_busy:
        raise HTTPException(400, 'Taskmanager is busy')
    bgtask.add_task(manager.execute_task, crawl_urls, manager, user, prod_urls, site_config)
    return 'Crawling started'


@router.get('/stoptask')
def stop_task(user: UserDependency):
    try:
        manager.stop()
    except Exception as e:
        raise HTTPException(400, str(e))
    return 'Task manager stopped'


@router.websocket('/taskstatus')
async def tws(socket: WebSocket):
    await socket.accept()
    manager.add_socket(socket)
    await manager.send_logs()
    try:
        while True:
            await socket.receive_text()
    except WebSocketDisconnect:
        manager.remove_socket(socket)


