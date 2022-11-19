from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

engine = create_async_engine("sqlite+aiosqlite:///bot.db")

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
