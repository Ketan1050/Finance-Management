from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(255))

    expenses = relationship("Expense", back_populates="owner")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    amount = Column(Float)
    category = Column(String(50))
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="expenses") 