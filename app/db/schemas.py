import datetime as dt
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict  # <- pydantic v2

# ===== Auth / User =====
class UserCreate(SQLModel):
    email: str = Field(description="E-mail do usuário (será usado como login).")
    password: str = Field(description="Senha do usuário.")
    full_name: Optional[str] = Field(default=None, description="Nome completo (opcional).")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "teste@example.com",
            "password": "SenhaF0rte!",
            "full_name": "Teste"
        }
    })

class UserRead(SQLModel):
    id: int
    email: str
    full_name: Optional[str] = None

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

# ===== Category =====
class CategoryBase(SQLModel):
    name: str = Field(description="Nome da categoria (único por usuário).")
    color: Optional[str] = Field(default=None, description="Cor hex da categoria (ex: #FF9900).")

class CategoryCreate(CategoryBase):
    model_config = ConfigDict(json_schema_extra={
        "example": {"name": "Alimentação", "color": "#FF9900"}
    })

class CategoryUpdate(SQLModel):
    name: Optional[str] = Field(default=None, description="Novo nome da categoria.")
    color: Optional[str] = Field(default=None, description="Nova cor hex.")

class CategoryRead(CategoryBase):
    id: int

# ===== Expense =====
class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    PIX = "PIX"
    TRANSFER = "TRANSFER"

class ExpenseStatus(str, Enum):
    PLANNED = "PLANNED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class ExpenseBase(SQLModel):
    category_id: Optional[int] = Field(default=None, description="ID da categoria (opcional).")
    amount: float = Field(description="Valor da despesa (Decimal 2 casas).")
    currency: str = Field(default="BRL", description="Moeda (ISO 4217).")
    description: Optional[str] = Field(default=None, description="Descrição livre.")
    date: dt.date = Field(description="Data de origem/planejamento da despesa (YYYY-MM-DD).")
    paid_at: Optional[dt.datetime] = Field(default=None, description="Quando foi paga (ISO 8601).")
    payment_method: PaymentMethod = Field(default=PaymentMethod.CARD, description="Meio de pagamento.")
    status: ExpenseStatus = Field(default=ExpenseStatus.PLANNED, description="Status atual da despesa.")

class ExpenseCreate(ExpenseBase):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "category_id": 1,
            "amount": 125.50,
            "currency": "BRL",
            "description": "Supermercado",
            "date": "2025-10-05",
            "paid_at": "2025-10-05T14:35:00",
            "payment_method": "CARD",
            "status": "PAID"
        }
    })

class ExpenseUpdate(SQLModel):
    category_id: Optional[int] = Field(default=None, description="Novo ID da categoria (opcional).")
    amount: Optional[float] = Field(default=None, description="Novo valor.")
    currency: Optional[str] = Field(default=None, description="Nova moeda ISO 4217.")
    description: Optional[str] = Field(default=None, description="Nova descrição.")
    date: Optional[dt.date] = Field(default=None, description="Nova data (YYYY-MM-DD).")
    paid_at: Optional[dt.datetime] = Field(default=None, description="Nova data/hora de pagamento.")
    payment_method: Optional[PaymentMethod] = Field(default=None, description="Novo meio de pagamento.")
    status: Optional[ExpenseStatus] = Field(default=None, description="Novo status.")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "amount": 150.75,
            "description": "Supermercado (frutas e laticínios)",
            "status": "PAID"
        }
    })

class ExpenseRead(ExpenseBase):
    id: int

# ---- Schemas de relatório (saída) ----
class MonthlyTotal(SQLModel):
    year: int
    month: int
    currency: str
    total_amount: float

class CategorySum(SQLModel):
    category_id: Optional[int]
    category_name: Optional[str]
    total_amount: float
