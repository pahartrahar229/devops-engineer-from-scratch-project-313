import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app import crud
from app.database import get_session
from app.schemas import LinkCreate, LinkRead, LinkUpdate

router = APIRouter(prefix='/api/links', tags=['links'])

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8080')


def build_short_url(short_name: str) -> str:
    return f'{BASE_URL}/r/{short_name}'


def to_read_schema(link) -> LinkRead:
    return LinkRead(
        id=link.id,
        original_url=link.original_url,
        short_name=link.short_name,
        short_url=build_short_url(link.short_name),
        created_at=link.created_at,
    )


def get_link_or_404(session: Session, link_id: int):
    link = crud.get_link(session, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail='Link not found')
    return link


@router.get('', response_model=list[LinkRead])
def list_links(session: Session = Depends(get_session)):
    links = crud.get_links(session)
    return [to_read_schema(link) for link in links]


@router.post('', response_model=LinkRead, status_code=201)
def create_link(
    data: LinkCreate, session: Session = Depends(get_session)
):
    try:
        link = crud.create_link(
            session, data.original_url, data.short_name
        )
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=422,
            detail=f"short_name '{data.short_name}' already exists",
        )
    return to_read_schema(link)


@router.get('/{link_id}', response_model=LinkRead)
def read_link(link_id: int, session: Session = Depends(get_session)):
    link = get_link_or_404(session, link_id)
    return to_read_schema(link)


@router.put('/{link_id}', response_model=LinkRead)
def replace_link(
    link_id: int,
    data: LinkUpdate,
    session: Session = Depends(get_session),
):
    link = get_link_or_404(session, link_id)
    try:
        link = crud.update_link(
            session, link, data.original_url, data.short_name
        )
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=422,
            detail=f"short_name '{data.short_name}' already exists",
        )
    return to_read_schema(link)


@router.delete('/{link_id}', status_code=204)
def remove_link(link_id: int, session: Session = Depends(get_session)):
    link = get_link_or_404(session, link_id)
    crud.delete_link(session, link)