from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Influencer(Base):
    __tablename__ = 'influencers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    niche = Column(String, nullable=False)
    followers = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Influencer(name='{self.name}', niche='{self.niche}', followers='{self.followers}')>",
