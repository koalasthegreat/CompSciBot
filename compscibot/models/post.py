from sqlalchemy import Column, Integer, BigInteger, DateTime

from compscibot.db import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    post_id = Column(BigInteger)
    user_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    timestamp = Column(DateTime)
