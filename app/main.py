import os

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

# Importar los modelos registra una sola vez todas las tablas en Base.metadata.
from app.database import get_db
from app.models import (  # noqa: F401
    branch,
    category,
    inventory,
    payment_method,
    product,
    sale,
    sale_detail,
    user,
)
from app.routers import (
    auth,
    branches,
    categories,
    inventory,
    payment_methods,
    products,
    reports,
    sales,
    users,
)

templates = Jinja2Templates(directory="app/templates")

app = FastAPI(title="Punto de Venta Multi-Sede")

session_secret = os.getenv("SESSION_SECRET")
if not session_secret:
    raise ValueError("No se encontro SESSION_SECRET")

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    same_site = "lax",
    https_only=os.getenv("RENDER") == "true",
)
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name = "static"
)

app.include_router(auth.router)
app.include_router(branches.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(payment_methods.router)
app.include_router(reports.router)


@app.get("/health", tags=["Sistema"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/")
def root():
    return RedirectResponse(url = "/login",status_code=302)

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "login.html",
    )

@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "dashboard.html",
    )

@app.get ("/sucursales-ui")
def branches_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "branches.html",
    )

@app.get("/productos-ui")
def products_page (request: Request):
    return  templates.TemplateResponse(
        request = request,
        name = "products.html",
    )

@app.get("/inventario-ui")
def inventory_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "inventory.html",
    )

@app.get("/ventas-ui")
def sales_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "sales.html",
    )

@app.get("/usuarios-ui")
def users_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "users.html",
    )

@app.get("/reportes-ui")
def reports_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "reports.html",
    )
