from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

app = FastAPI()

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request=request,name="dashboard.html")