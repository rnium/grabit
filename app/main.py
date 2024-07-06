from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from app.dependencies import DbDependency
from app.routers import auth, product
from app.scraping.websites import site_list

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    sites = [{site['name']: site['urlpatterns']}for site in site_list]
    return {'message': 'Welcome to GrabFast', 'available_websites': sites}