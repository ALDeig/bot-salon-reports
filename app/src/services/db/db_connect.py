from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine


def create_engine(db_url: str):
    engine = create_async_engine(db_url, echo=True)
    return engine


def create_session_factory(db_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    return async_session
 

