from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.v1.api import api_router
from src.app.core.config import settings


app = FastAPI(
    title="CozyCash API",
    description="A cozy expenses tracker API with Clean Architecture",
    version="1.0.0",
    openapi_url=(
        f"{settings.api_v1_str}/openapi.json"
        if hasattr(settings, "api_v1_str")
        else "/openapi.json"
    ),
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

templates = Jinja2Templates(directory="src/templates")

app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/expenses", response_class=HTMLResponse)
async def expenses_page(request: Request):
    return templates.TemplateResponse("expenses.html", {"request": request})


@app.get("/budgets", response_class=HTMLResponse)
async def budgets_page(request: Request):
    return templates.TemplateResponse("budgets.html", {"request": request})
