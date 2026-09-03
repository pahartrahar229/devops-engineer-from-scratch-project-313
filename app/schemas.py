from datetime import datetime

from sqlmodel import SQLModel


class LinkCreate(SQLModel):
    original_url: str
    short_name: str


class LinkUpdate(SQLModel):
    original_url: str
    short_name: str


class LinkRead(SQLModel):
    id: int
    original_url: str
    short_name: str
    short_url: str
    created_at: datetime