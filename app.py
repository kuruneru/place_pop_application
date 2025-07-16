from fastapi import FastAPI, Request, Form
from sqlalchemy import create_engine, text
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
import os


app = FastAPI()
db_url = os.getenv("DATABASE_URL")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def first(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages})