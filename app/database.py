import os

from sqlmodel import Session, SQLModel, create_engine


def normalize_database_url(url):
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+psycopg://', 1)
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url


raw_database_url = os.environ.get('DATABASE_URL', '').strip()
if not raw_database_url:
    raw_database_url = 'sqlite:///./app.db'

DATABASE_URL = normalize_database_url(raw_database_url)

connect_args = (
    {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}
)

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
except Exception as error:
    raise RuntimeError(
        f"Failed to create database engine from DATABASE_URL "
        f"(value after normalization: {DATABASE_URL!r}). "
        f"Check that the DATABASE_URL environment variable is set "
        f"correctly. Original error: {error}"
    ) from error


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session