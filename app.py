from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse 
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import upload
import cloudinary
import os
import uuid
import shutil
import bcrypt
import random

# cloudinaryの初期設定
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

#定義やインスタンス化
app = FastAPI()
db_url = os.getenv("DATABASE_URL")
templates = Jinja2Templates(directory="templates")
post_page = Jinja2Templates(directory="templates")
engine = create_engine(db_url)

def make_id():
    text = "AAAAAAAAAAAAAAAA"
    for i in text:
        limit = 122 - chr(ord(i))
        rand_num = random(0, limit)
        chr(ord(i) + rand_num)
    print(f">> {text}")
    return text

make_id()

#メインページが開かれたとき
@app.get("/")
def first(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "messages": "messages"})

#ユーザー登録ページが開かれたとき
@app.get("/user")
def post_form(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})

#ユーザー登録の流れ
@app.post("/user")
def user_registration(username: str = Form(...), email: str = Form(...), password: str = Form(...), profile: str = Form(None)):

    #パスワードのハッシュ化
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    #idは前に@を記述する
    id = f"@{username}"

    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("INSERT INTO users (id, username, email, password_hash, profile) VALUES (:id, :username, :email, :password_hash, :profile)"),
                {
                    "id": id,
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "profile": profile
                }
            )
            return RedirectResponse("/", status_code=303)
    except IntegrityError as e:
        print(f"Error during user registration: {e}")
        raise HTTPException(
            status_code=409, # Conflict
            detail="ユーザー名またはメールアドレス、または生成されたIDが既に存在します。別のものを試してみてください。"
        )
    except Exception as e:
        print(f"Error during user registration: {e}")
        raise HTTPException(status_code=500, detail=f"ユーザー登録中に予期せぬエラーが発生しました: {e}")

#ログイン画面の作成
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html",{"request": request})

@app.post("/login", response_class=HTMLResponse)
def login_system(username_or_email  : str = Form(...), password: str = Form(...)):
    user = None
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, username, email, password_hash FROM users WHERE username = :identifier OR email = :identifier"),
            {"identifier": username_or_email}
        )
    user = result.fetchone() #1行のみの取得
    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            print(f"ユーザー '{user.username}' がログインしました。")
            return RedirectResponse("/", status_code=303)
        else:
            print(f"ユーザー '{username_or_email}' のパスワードが間違っています。")
            error_message = "ユーザー名またはパスワードが正しくありません。"
    else:
        #ユーザが見つからない場合
        print(f"ユーザー '{username_or_email}' が見つかりません。")
        error_message = "ユーザー名またはパスワードが正しくありません。"
    
    #ログインページの再表示
    return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})

#投稿用ページが開かれたとき
@app.get("/post")
def post_form(request: Request):
    return templates.TemplateResponse("post.html", {"request": request})

#投稿用ページから投稿についての処理が行われたとき
@app.post("/post")
async def post_data(user_id: str = Form(...), title: str = Form(...), place_name: str = Form(...), address: str = Form(), image_file: UploadFile = File(...)):#これによりデータを受け取る

    upload_file = await image_file.read()

    # Upload an image
    upload_result = cloudinary.uploader.upload(upload_file,public_id="background")
    print(upload_result["secure_url"])

    # Optimize delivery by resizing and applying auto-format and auto-quality
    optimize_url, _ = cloudinary_url("bachground", fetch_format="auto", quality="auto")
    print(optimize_url)

    # Transform the image: auto-crop to square aspect_ratio
    auto_crop_url, _ = cloudinary_url("bachground", width=500, height=500, crop="auto", gravity="auto")
    print(auto_crop_url)

    try:
        with engine.begin() as conn:
            row = conn.execute(text("SELECT COUNT(*) FROM posts;"))
            row_count = row.scalar()

            print(row_count)

            result = conn.execute(
                text("INSERT INTO posts (id, user_id, title, place_name, address) VALUES (:id, :user_id, :title, :place_name, :address)"),
                {
                    "id": row_count,
                    "user_id": user_id,
                    "title": title,
                    "place_name": place_name,
                    "address": address
                }
            )
            return RedirectResponse("/", status_code=303)
    except IntegrityError as e:
        print(f"Error during user registration: {e}")
        raise HTTPException(
            status_code=409, # Conflict
            detail="ユーザー名またはメールアドレス、または生成されたIDが既に存在します。別のものを試してみてください。"
        )
    except Exception as e:
        print(f"Error during user registration: {e}")
        raise HTTPException(status_code=500, detail=f"投稿中に予期せぬエラーが発生しました: {e}")

