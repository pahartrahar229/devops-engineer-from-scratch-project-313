from sqlmodel import Session, func, select

from app.models import Link


def get_links(session: Session):
    statement = select(Link).order_by(Link.id)
    return session.exec(statement).all()


def count_links(session: Session) -> int:
    statement = select(func.count()).select_from(Link)
    return session.exec(statement).one()


def get_links_range(session: Session, start: int, limit: int):
    statement = (
        select(Link).order_by(Link.id).offset(start).limit(limit)
    )
    return session.exec(statement).all()


def get_link(session: Session, link_id: int):
    return session.get(Link, link_id)


def get_link_by_short_name(session: Session, short_name: str):
    statement = select(Link).where(Link.short_name == short_name)
    return session.exec(statement).first()


def create_link(session: Session, original_url: str, short_name: str):
    link = Link(original_url=original_url, short_name=short_name)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def update_link(
    session: Session, link: Link, original_url: str, short_name: str
):
    link.original_url = original_url
    link.short_name = short_name
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def delete_link(session: Session, link: Link):
    session.delete(link)
    session.commit()