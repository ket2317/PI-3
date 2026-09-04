from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


# Importar los modelos registra una sola vez todas las tablas en Base.metadata.

from app.routers import auth, branches, categories, products, users
from app.routers import inventory
from app.routers import payment_methods
from app.routers import sales


templates = Jinja2Templates(directory="app/templates")

app = FastAPI()
app.include_router(auth.router)
app.include_router(branches.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(inventory.router)
app.include_router(payment_methods.router)
app.include_router(sales.router)

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")
