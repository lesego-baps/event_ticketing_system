from fastapi import FastAPI
from database import create_db_tables
from routes import auth, events, tickets

app = FastAPI(title="Event Ticketing System")

@app.on_event("startup")
def on_startup():
    create_db_tables()

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(tickets.router)

@app.get("/")
def read_root():
    return {"message":"Event Ticket System API is running"}
