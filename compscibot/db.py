from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from compscibot.config import DB_PATH

Base = declarative_base()

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
