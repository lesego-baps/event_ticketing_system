from .connection import Base, SessionLocal, engine, get_db


def create_db_tables():
    Base.metadata.create_all(bind=engine)
