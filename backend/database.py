from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def get_engine(database_url):
    """Create a new SQLAlchemy engine."""
    engine = create_engine(database_url)
    return engine

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    email = Column(String(50))


def create_database(engine):
    """Create all tables in the database if they don't already exist."""
    Base.metadata.create_all(engine)


def get_session(engine):
    """Create a new session for the provided engine."""
    Session = sessionmaker(bind=engine)
    return Session()