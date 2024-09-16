from compscibot.config import DB_URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

engine = create_async_engine(f"sqlite+aiosqlite://{DB_URL}")

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
