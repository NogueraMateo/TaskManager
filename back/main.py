from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .routers import tasks_router, users_router, authenticate_users
from . import  models
from .database import SessionLocal, engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
# Run server "uvicorn back.main:app --reload"

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5500/front/sign_up.html?",
    "http://127.0.0.1:5500/front/login.html",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite todas las origenes para desarrollo, ajusta según necesidad
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

jinja2_template = Jinja2Templates(directory="front")

app.include_router(authenticate_users.router)
app.include_router(users_router.router)
app.include_router(tasks_router.router)
app.mount("/statics", StaticFiles(directory="front/statics"), name="statics")



@app.get("/", response_class=HTMLResponse)
def root(request : Request):
    return jinja2_template.TemplateResponse("login.html", {"request" : request})


@app.get("/dashboard", response_class= HTMLResponse)
async def dashboard(request: Request, user: models.User = Depends(authenticate_users.get_current_user)):
    return jinja2_template.TemplateResponse("dashboard.html", {"request": request, "user": user})


@app.get("/sign_up", response_class= HTMLResponse)
async def signup(request: Request):
    return jinja2_template.TemplateResponse('sign_up.html', {"request": request})








