from sqlmodel import Session, select
from models import Event 
def get_all_events(session: Session):
    return session.exec(select(Event)).all()
def get_event_by_id(session: Session, event_id:int):
    return session.get(Event, event_id)
def create_ecvent( session: Session, event_data: dict):
    event = Event(**event_data)
    session.add(event)
    session.commit()
    session.refresh()
    return event
