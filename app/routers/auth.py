from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models import User
from app.db.schemas import UserCreate, UserRead, Token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria um novo usuário com e-mail único e retorna seus dados básicos.",
    response_description="Dados do usuário criado."
)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead(id=user.id, email=user.email, full_name=user.full_name)

@router.post(
    "/login",
    response_model=Token,
    summary="Login com e-mail e senha",
    description=(
        "Autentica o usuário usando **form-urlencoded** (`username`, `password`) e retorna o token JWT.\n\n"
        "Use o botão **Authorize** no Swagger e cole `Bearer SEU_TOKEN` para testar rotas protegidas."
    ),
    response_description="Token de acesso (JWT)."
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token(subject=user.email)
    return Token(access_token=token)

@router.get(
    "/me",
    response_model=UserRead,
    summary="Dados do usuário autenticado",
    description="Retorna as informações básicas do usuário associado ao token fornecido.",
    response_description="Perfil do usuário autenticado."
)
def me(current_user: User = Depends(get_current_user)):
    return UserRead(id=current_user.id, email=current_user.email, full_name=current_user.full_name)
