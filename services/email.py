import base64
import io
import secrets
from datetime import timedelta
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from passlib.context import CryptContext
import qrcode
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.connection import Base, engine, get_db
from dependencies import create_access_token, get_admin_user, get_current_user, settings
from models import Event, Ticket, User
from schemas import EventCreate, EventOut, TicketOut, Token, UserCreate, UserLogin, UserOut
from services.email import send_ticket_email


def generate_ticket_code() -> str:
    return secrets.token_urlsafe(12)


def generate_qr_code(ticket_code: str) -> str:
    qr = qrcode.make(ticket_code)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

app = FastAPI(title="Event Ticket System")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

@app.get("/")
async def root():
    return {"message": "Event Ticket System API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/auth/register", response_model=UserOut)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = User(
        email=user.email.lower(),
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        is_admin=False,
    )
    db.add(db_user)

    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Registration failed")

    return db_user

@app.post("/auth/login", response_model=Token)
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}

@app.post("/events", response_model=EventOut)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    new_event = Event(
        title=event.title,
        description=event.description,
        venue=event.venue,
        event_date=event.event_date,
        organizer_id=current_user.id,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@app.get("/events", response_model=list[EventOut])
async def list_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@app.post("/events/{event_id}/tickets", response_model=TicketOut)
async def create_ticket_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    ticket_code = generate_ticket_code()
    new_ticket = Ticket(
        code=ticket_code,
        user_id=current_user.id,
        event_id=event.id,
        is_used=False,
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    qr_data_url = generate_qr_code(ticket_code)

    await send_ticket_email(
        email=current_user.email,
        event_title=event.title,
        ticket_code=ticket_code,
        qr_data_url=qr_data_url,
    )

    return new_ticket

@app.get("/tickets/me", response_model=list[TicketOut])
async def my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Ticket).filter(Ticket.user_id == current_user.id).all()
