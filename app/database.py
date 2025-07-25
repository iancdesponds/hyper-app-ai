#database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base

from models import TrainExerciseView, TrainingAvailability


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Defina a env var DATABASE_URL")

# engine = create_engine(DATABASE_URL, connect_args={"ssl": {"ca": "ca.pem"}})
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": {"ca": "ca.pem"}},
    pool_pre_ping=True,
    pool_recycle=3600,  # recicla conexões antigas
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()