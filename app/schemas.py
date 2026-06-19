from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID


# =========================
# USER SCHEMAS
# =========================

class UserAuth(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# =========================
# EXPENSE SCHEMAS
# =========================

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str] = None


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: UUID
    title: str
    amount: float
    category: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# SUMMARY SCHEMA
# =========================

class ExpenseSummary(BaseModel):
    total_spent: float
    total_transactions: int
    category_breakdown: Dict[str, float]


class ExpenseOut(BaseModel):
    id: UUID
    title: str
    amount: float
    category: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True 
# =========================
# LOGIN SCHEMA
# =========================

class LoginSchema(BaseModel):
    email: EmailStr
    password: str 