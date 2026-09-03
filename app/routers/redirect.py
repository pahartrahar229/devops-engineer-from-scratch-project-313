from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app import crud
from app.database import get_session

router = APIRouter(tags=['redirect'])


@router.get('/r/{short_name}')
def redirect_to_original(
    short_name: str, session: Session = Depends(get_session)
):
    link = crud.get_link_by_short_name(session, short_name)
    if link is None:
        raise HTTPException(status_code=404, detail='Link not found')
    return RedirectResponse(url=link.original_url, status_code=302)