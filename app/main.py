from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from app.routers.auth import router as auth_router
from app.routers import branches


templates = Jinja2Templates(directory="app/templates")

app = FastAPI()
app.include_router(auth_router)
app.include_router(branches.router)

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request=request,name="dashboard.html")