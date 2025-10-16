from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db, get_current_user
from app.db.models import Category, User
from app.db.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
    description="Cria uma nova categoria **única por usuário**.",
    response_description="Categoria criada."
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exists = (
        db.query(Category)
        .filter(Category.user_id == current_user.id, Category.name == payload.name)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    obj = Category(user_id=current_user.id, name=payload.name, color=payload.color)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return CategoryRead(id=obj.id, name=obj.name, color=obj.color)

@router.get(
    "",
    response_model=List[CategoryRead],
    summary="Listar categorias",
    description="Retorna todas as categorias do usuário autenticado, ordenadas por nome.",
    response_description="Lista de categorias."
)
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.query(Category).filter(Category.user_id == current_user.id).order_by(Category.name).all()
    return [CategoryRead(id=r.id, name=r.name, color=r.color) for r in rows]

@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Buscar categoria por ID",
    description="Retorna a categoria correspondente ao `category_id` do usuário autenticado.",
    response_description="Categoria encontrada."
)
def get_category(
    category_id: int = Path(..., description="ID da categoria."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryRead(id=obj.id, name=obj.name, color=obj.color)

@router.put(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Atualizar categoria",
    description="Atualiza **nome** e/ou **cor** de uma categoria.",
    response_description="Categoria atualizada."
)
def update_category(
    category_id: int = Path(..., description="ID da categoria."),
    payload: CategoryUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.name is not None:
        conflict = (
            db.query(Category)
            .filter(Category.user_id == current_user.id, Category.name == payload.name, Category.id != category_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=400, detail="Another category with this name already exists")
        obj.name = payload.name
    if payload.color is not None:
        obj.color = payload.color
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return CategoryRead(id=obj.id, name=obj.name, color=obj.color)

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria",
    description="Remove a categoria do usuário autenticado. Despesas atreladas ficam com `category_id` nulo (se você configurou assim no banco)."
)
def delete_category(
    category_id: int = Path(..., description="ID da categoria."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(obj)
    db.commit()
    return None
