"""
Main Application Entry Point.

This module initializes the FastAPI application, configures global settings,
middleware (CORS), static file serving, and template rendering. It also mounts
the API routers and defines the endpoints for serving HTML frontend pages.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.v1.api import api_router
from src.app.core.config import settings


app = FastAPI(
    title="CozyCash API",
    description="""
A modern, clean-architecture based API for expense tracking and budget management.
        
## Features
* **Authentication**: Secure login/signup with JWT tokens.
* **Expenses**: Track daily spending with categories and detailed descriptions.
* **Budgets**: Set monthly limits per category to maintain financial health.
* **Analytics**: Real-time dashboard with trend charts and category breakdowns.
        
Built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.
""",
    version="1.0.0",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url=f"{settings.api_v1_str}/docs",
)

# CORS Configuration
# Restricts requests to allowed origins to prevent unauthorized browser access.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Configure Template Engine (Jinja2) for HTML rendering
templates = Jinja2Templates(directory="src/templates")

# Include API Router (all endpoints under /api/v1)
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the Landing Page (Home).
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    """
    Serves the Authentication Page (Login/Signup).
    """
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """
    Serves the Main Dashboard Page.
    Displays summary cards, charts, and recent activity.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/expenses", response_class=HTMLResponse)
async def expenses_page(request: Request):
    """
    Serves the Expenses Management Page.
    Allows users to view, add, edit, and delete expenses.
    """
    return templates.TemplateResponse("expenses.html", {"request": request})


@app.get("/budgets", response_class=HTMLResponse)
async def budgets_page(request: Request):
    """
    Serves the Budgets Management Page.
    Allows users to set and track spending limits.
    """
    return templates.TemplateResponse("budgets.html", {"request": request})
