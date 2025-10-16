import datetime as dt
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.db.models import Expense, User
from app.db.schemas import (
    ExpenseCreate, ExpenseRead, ExpenseUpdate,
    MonthlyTotal, CategorySum
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.post(
    "",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar despesa",
    description="Cria uma nova despesa associada ao usuário autenticado.",
    response_description="Despesa criada."
)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = Expense(user_id=current_user.id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ExpenseRead(**obj.model_dump())

@router.get(
    "",
    response_model=List[ExpenseRead],
    summary="Listar despesas com filtros",
    description=(
        "Retorna despesas do usuário autenticado, com suporte a filtros de **período**, **categoria**, "
        "**status** e **faixa de valores**, além de **paginação**."
    ),
    response_description="Lista de despesas."
)
def list_expenses(
    start: Optional[dt.date] = Query(None, description="Data inicial (inclusiva) no formato YYYY-MM-DD.", examples=["2025-10-01"]),
    end: Optional[dt.date] = Query(None, description="Data final (inclusiva) no formato YYYY-MM-DD.", examples=["2025-10-31"]),
    category_id: Optional[int] = Query(None, description="Filtra por ID de categoria."),
    status: Optional[str] = Query(None, description="Filtra por status: PLANNED | PAID | CANCELLED."),
    min: Optional[float] = Query(None, description="Valor mínimo."),
    max: Optional[float] = Query(None, description="Valor máximo."),
    page: int = Query(1, description="Página (base 1).", ge=1),
    size: int = Query(20, description="Tamanho da página.", ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Expense).filter(Expense.user_id == current_user.id)
    if start:
        q = q.filter(Expense.date >= start)
    if end:
        q = q.filter(Expense.date <= end)
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    if status:
        q = q.filter(Expense.status == status)
    if min is not None:
        q = q.filter(Expense.amount >= min)
    if max is not None:
        q = q.filter(Expense.amount <= max)

    items = q.order_by(Expense.date.desc(), Expense.id.desc()).offset((page - 1) * size).limit(size).all()
    return [ExpenseRead(**i.model_dump()) for i in items]

@router.get(
    "/{expense_id}",
    response_model=ExpenseRead,
    summary="Buscar despesa por ID",
    description="Retorna a despesa correspondente ao `expense_id` do usuário autenticado.",
    response_description="Despesa encontrada."
)
def get_expense(
    expense_id: int = Path(..., description="ID da despesa."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseRead(**obj.model_dump())

@router.put(
    "/{expense_id}",
    response_model=ExpenseRead,
    summary="Atualizar despesa",
    description="Atualiza campos específicos da despesa (parcial) para o `expense_id` informado.",
    response_description="Despesa atualizada."
)
def update_expense(
    expense_id: int = Path(..., description="ID da despesa."),
    payload: ExpenseUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Expense not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ExpenseRead(**obj.model_dump())

@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir despesa",
    description="Remove a despesa do usuário autenticado."
)
def delete_expense(
    expense_id: int = Path(..., description="ID da despesa."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(obj)
    db.commit()
    return None

# ===== Reports (lendo suas views) =====

@router.get(
    "/summary/monthly",
    response_model=List[MonthlyTotal],
    tags=["Reports"],
    summary="Totais mensais por ano",
    description="Retorna a soma dos valores **por mês** e **moeda**, filtrável por ano.",
    response_description="Lista de totais mensais."
)
def monthly_totals(
    year: Optional[int] = Query(None, description="Ano alvo. Se omitido, retorna todos os anos."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sql = """
        SELECT EXTRACT(YEAR FROM date) AS year,
               EXTRACT(MONTH FROM date) AS month,
               currency,
               SUM(amount) AS total_amount
        FROM v_expenses_basic
        WHERE user_id = :user_id
          AND status <> 'CANCELLED'
          {year_clause}
        GROUP BY EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date), currency
        ORDER BY year, month
    """
    year_clause = "AND EXTRACT(YEAR FROM date) = :year" if year else ""
    q = text(sql.format(year_clause=year_clause))
    params = {"user_id": current_user.id}
    if year:
        params["year"] = year
    rows = db.execute(q, params).mappings().all()
    return [
        MonthlyTotal(
            year=int(r["year"]),
            month=int(r["month"]),
            currency=r["currency"],
            total_amount=float(r["total_amount"])
        )
        for r in rows
    ]

@router.get(
    "/summary/by-category",
    response_model=List[CategorySum],
    tags=["Reports"],
    summary="Totais por categoria (período)",
    description="Soma valores **por categoria** em um intervalo opcional de datas (`start`, `end`).",
    response_description="Lista de totais por categoria."
)
def by_category(
    start: Optional[dt.date] = Query(None, description="Data inicial (YYYY-MM-DD)."),
    end: Optional[dt.date] = Query(None, description="Data final (YYYY-MM-DD)."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sql = """
        SELECT e.category_id,
               b.category_name,
               SUM(e.amount) AS total_amount
        FROM v_expenses_basic b
        JOIN expenses e ON e.id = b.id
        WHERE e.user_id = :user_id
          AND e.status <> 'CANCELLED'
          {start_clause}
          {end_clause}
        GROUP BY e.category_id, b.category_name
        ORDER BY total_amount DESC
    """
    start_clause = "AND e.date >= :start" if start else ""
    end_clause = "AND e.date <= :end" if end else ""
    q = text(sql.format(start_clause=start_clause, end_clause=end_clause))
    params = {"user_id": current_user.id}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    rows = db.execute(q, params).mappings().all()
    return [
        CategorySum(
            category_id=r["category_id"],
            category_name=r["category_name"],
            total_amount=float(r["total_amount"])
        )
        for r in rows
    ]
