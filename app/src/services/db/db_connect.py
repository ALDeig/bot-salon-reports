from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


def create_engine(db_url: str):
    engine = create_async_engine(db_url, future=True, echo=False)
    return engine


def create_session(db_url: str):
    engine = create_engine(db_url)
    db_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return db_pool

