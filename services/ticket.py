from sqlmodel import Session, select
from models import Ticket, Event
import uuid
import qrcode
from io import BytesIO
import base64

def create_ticket(session: Session, user_id: int, event_id: int):
    event = session.get(Event, event_id)
    if not event:
        raise ValueError("Event not found")

    #check capacity
    existing = session.exec(select(Ticket).where(Ticket.event_id==event_id)).all()
    if len(existing) >= event.capacity:
        raise ValueError("Event sold out")

    ticket =Ticket(
        id=str(uuid.uuid4())[:8].upper(),
        user_id= user_id,
        event_id=event_id,
        is_used=False
    )
    session.add(ticket)
    session.commit()
    session.refresh()
    return ticket
def generate_qr_base64(ticket_id:str):
    img = qrcode.make(ticket_id)
    buffer= BytesIO
    img.save(buffer, format= "PNG")
    return base64.b64encode(buffer.getvalue()).decode()
