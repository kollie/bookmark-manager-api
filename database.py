from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

# Load environment variables from the .env file.
load_dotenv()

# Retrieve the database URL from environment variables.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookmarks.db")

# Create the SQLAlchemy engine.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions.
Base = declarative_base()

def init_db():
    """
    Initialize the database and apply migrations.
    """
    # Create all tables based on the model definitions.
    Base.metadata.create_all(bind=engine)
    
    # Configure and run the Alembic migration to the latest version.
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

def get_db():
    """
    Dependency function to provide a database session.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
