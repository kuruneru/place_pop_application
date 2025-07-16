from fastapi import FastAPI, Request, Form
from sqlalchemy import create_engine, text
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
import os
