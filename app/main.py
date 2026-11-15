
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.connection import Base, engine
from app.database import models

from app.routes import auth, access, venues, events, tickets, hire
from app.routes import bookings, waitlist, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("EventSphere database initialized successfully!")
    yield


app = FastAPI(
    title="EventSphere",
    description="Multi-Agent Event and Venue Booking Platform",
    version="1.0.0",
    lifespan=lifespan
)


# Static files and HTML templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


# Common Login Page
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


# Admin Dashboard Page
@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={}
    )


# Attendee Dashboard Page
@app.get("/attendee", response_class=HTMLResponse)
def attendee_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="attendee.html",
        context={}
    )


# Gate Staff Scanner Page
@app.get("/scanner", response_class=HTMLResponse)
def scanner_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="scanner.html",
        context={}
    )


# Register API routes
app.include_router(auth.router)
app.include_router(access.router)
app.include_router(venues.router)
app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(bookings.router)
app.include_router(hire.router)
app.include_router(waitlist.router)
app.include_router(dashboard.router)


# Application Home
@app.get("/")
def home():
    return RedirectResponse(url="/login")


@app.get("/health")
def health_check():
    return {"status": "healthy"}
