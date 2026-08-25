from fastapi import FastAPI
from routers.products import router as products_router
from routers.sucursales import router as sucursales_router

app = FastAPI()

app.include_router(products_router)
app.include_router(sucursales_router)


@app.get("/")
def root():
    return {"message": "Proyecto integrador funcionando"}
