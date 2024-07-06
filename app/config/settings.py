from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv()


DB_URL = os.getenv('DB_URL', 'sqlite:///./db.sqlite3')
DB_CONNECT_ARGS = {}
if DB_URL.startswith('sqlite'):
    DB_CONNECT_ARGS['check_same_thread'] = False

SECRET_KEY = "71751bbc7b6adf880cc183eb76f0191fd01379b8a2a053380049ac749dbaeba4"
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

try:
    from .local_settings import *
except ImportError:
    pass