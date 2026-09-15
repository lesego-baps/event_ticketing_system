from .connection import Base, SessionLocal, engine

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)