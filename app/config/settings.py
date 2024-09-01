from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv()


DB_URL = os.getenv('DB_URL', 'postgresql://postgres:postgres@db/postgres')
DB_CONNECT_ARGS = {}
if DB_URL.startswith('sqlite'):
    DB_CONNECT_ARGS['check_same_thread'] = False

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_MINUTES = 1440
REQUESTS_USER_AGENT = os.getenv('USER_AGENT')

try:
    from .local_settings import *
except ImportError:
    pass