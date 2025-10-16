from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, categories, expenses

openapi_tags = [
    {"name": "Auth", "description": "Rotas de autenticação e identificação do usuário."},
    {"name": "Categories", "description": "CRUD de categorias de despesas do usuário."},
    {"name": "Expenses", "description": "CRUD de despesas e relatórios."},
    {"name": "Reports", "description": "Sumários e agregações para insights financeiros."},
    {"name": "Health", "description": "Checagens simples de disponibilidade do serviço."},
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API RESTful para **gestão de despesas pessoais**, com autenticação JWT. "
        "Use o botão **Authorize** no topo do Swagger para testar as rotas protegidas."
    ),
    contact={
        "name": "João Pedro Queiroz Viana",
        "url": "https://github.com/Joao-Pedro-Queiroz",
        "email": "jpqv0105@gmail.com",
    },
    openapi_tags=openapi_tags,
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)

@app.get("/health", tags=["Health"], summary="Healthcheck", description="Retorna `ok` se o serviço está respondendo.")
async def health():
    return {"status": "ok"}
