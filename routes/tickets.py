import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import Event, Ticket, User
from schemas import TicketOut

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/events/{event_id}", response_model=TicketOut)
def create_ticket(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.get(Event, event_id) is None:
        raise HTTPException(status_code=404, detail="Event not found")

    ticket = Ticket(code=secrets.token_urlsafe(12), user_id=current_user.id, event_id=event_id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/me", response_model=list[TicketOut])
def list_my_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Ticket).filter(Ticket.user_id == current_user.id).all()