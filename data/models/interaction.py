from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from . import Base

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
