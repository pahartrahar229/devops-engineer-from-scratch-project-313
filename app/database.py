import os

from sqlmodel import Session, SQLModel, create_engine


def normalize_database_url(url):
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+psycopg://', 1)
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url


DATABASE_URL = normalize_database_url(
    os.environ.get('DATABASE_URL', 'sqlite:///./app.db')
)

connect_args = (
    {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}
)

engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session