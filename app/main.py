from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from app.dependencies import DbDependency
from app.routers import auth, product
from app.scraping.websites import site_list
from app.config.settings import BASE_DIR
import os

app = FastAPI(
    title='GrabIT',
    description='Scrape and store IT product data',
    version='0.1.0'
)

app.include_router(product.router)
app.include_router(auth.router)


allowed_origins = [
    'http://localhost:3030',
    'http://127.0.0.1:3030',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]


if remote:=os.getenv('CORS_ALLOW_HOST'):
    allowed_origins.append(remote)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/{full_path:path}')
async def root(full_path: str):
    if full_path == '':
        return FileResponse(BASE_DIR / 'frontend' / 'index.html')
    file_path = BASE_DIR / 'frontend' / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    else:
        return HTTPException(status_code=404)