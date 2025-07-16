from fastapi import FastAPI, Request, Form
from sqlalchemy import create_engine, text
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
import os


app = FastAPI()
db_url = os.getenv("DATABASE_URL")

@app.get("/")
def first():
    return {"message": "Hello World"}