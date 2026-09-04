from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(settings.database_url, echo=False)


def create_db_and_tables() -> None:
    """Only used for initial local bring-up / quick checks.
    Real schema changes should go through Alembic migrations, not this.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session