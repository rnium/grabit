from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings
class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DB_URL, connect_args=settings.DB_CONNECT_ARGS)

SessionLocal = sessionmaker(autoflush=False, bind=engine)