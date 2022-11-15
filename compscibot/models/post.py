from typing import Any, Optional

from sqlalchemy import BigInteger, Column, DateTime, Integer, Text, select

from compscibot.db import Base, async_session


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    post_id = Column(BigInteger)
    user_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    timestamp = Column(DateTime)
    channel_id = Column(BigInteger)
    content = Column(Text)
    star_count = Column(Integer)

    @classmethod
    async def get_by_post(cls, post_id: int) -> Optional["Post"]:
        async with async_session() as session:
            result = await session.execute(select(Post).filter_by(post_id=post_id))

            return result.scalars().first()

    @classmethod
    async def add(cls, **kwargs: Any) -> "Post":
        instance = cls(**kwargs)

        async with async_session() as session:
            async with session.begin():
                session.add(instance)
                await session.commit()

        return instance
