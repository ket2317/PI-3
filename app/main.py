import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# Importar los modelos registra una sola vez todas las tablas en Base.metadata.
from app.models import branch, category, inventory, product, user  # noqa: F401
from app.routers import auth, branches, categories, inventory, products, users

templates = Jinja2Templates(directory="app/templates")

app = FastAPI(title="Punto de Venta Multi-Sede")

session_secret = os.getenv("SESSION_SECRET")
if not session_secret:
    raise ValueError("No se encontro SESSION_SECRET")

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    same_site = "lax",
    https_only = False
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
