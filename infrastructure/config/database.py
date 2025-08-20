import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True  # In ra SQL để debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho models
Base = declarative_base()

# Dependency cho FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
