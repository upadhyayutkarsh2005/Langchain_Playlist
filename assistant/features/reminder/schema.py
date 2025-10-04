from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///./reminders.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)
    remind_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# -------------------------
# Pydantic Schemas
# -------------------------
class ReminderIn(BaseModel):
    text: str  # natural language input

class ReminderOut(BaseModel):
    id: int
    task: str
    remind_at: datetime
    created_at: datetime