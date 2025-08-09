from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite+aiosqlite.///./test.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True 
)

AsyncSessionLocal = async_sessionmaker(
    bind=AsyncSession,
    class_= AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all) 
