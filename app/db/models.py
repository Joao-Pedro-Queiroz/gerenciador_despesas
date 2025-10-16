from datetime import datetime, date
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field

class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    PIX = "PIX"
    TRANSFER = "TRANSFER"

class ExpenseStatus(str, Enum):
    PLANNED = "PLANNED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    password_hash: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Expense(SQLModel, table=True):
    __tablename__ = "expenses"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    amount: float
    currency: str = Field(default="BRL", max_length=3)
    description: Optional[str] = None
    date: date
    paid_at: Optional[datetime] = None
    payment_method: PaymentMethod = Field(default=PaymentMethod.CARD)
    status: ExpenseStatus = Field(default=ExpenseStatus.PLANNED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)