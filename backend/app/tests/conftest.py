"""
Tests run against a throwaway SQLite database (not the dev Postgres DB) so
they're fast and fully isolated. The app code itself is DB-agnostic
(SQLAlchemy Core types only), which is what makes this swap safe.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
import app.models  # noqa: F401 registers all models


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
