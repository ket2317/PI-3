from fastapi import FastAPI
from routers.products import router as products_router
from routers.branches import router as sucursales_router
from routers.users import router as users_router
from models.category import Category
from models.role import Role
from routers.categories import router as categories_router

app = FastAPI()

app.include_router(products_router)
app.include_router(sucursales_router)
app.include_router(users_router)
app.include_router(categories_router)


@app.get("/")
def root():
    return {"message": "Proyecto integrador funcionando"}
