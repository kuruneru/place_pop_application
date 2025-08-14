from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse 
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import upload
from starlette.middleware.sessions import SessionMiddleware
import cloudinary
import itsdangerous
import os
import bcrypt
import random, string

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
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

#ランダムなIDの生成関数
def make_id(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

#メインページが開かれたとき
@app.get("/")
async def first(request: Request):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM posts"))
        rows = result.fetchall()
        posts = [dict._mapping(row) for row in rows]
        
    return templates.TemplateResponse("index.html", {"request": request, "post_info": posts})

#ユーザー登録ページが開かれたとき
@app.get("/user")
def post_form(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})

#ユーザ登録の処理
@app.post("/user")
def user_registration(username: str = Form(...), email: str = Form(...), password: str = Form(...), profile: str = Form(None)):

    # パスワードのハッシュ化
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with engine.begin() as conn:
            # ランダム生成した文字列が使われていないかを確認
            id_check = True
            while id_check:
                id = make_id(16)
                id_check = conn.execute(
                    text("SELECT EXISTS (SELECT 1 FROM users WHERE id = :id)"),
                    {"id": id}
                ).scalar()

            id = "@" + id

            # メールアドレスとIDが両方存在するかチェック
            duplicate_check = conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1 FROM users
                        WHERE email = :email
                    )
                """),
                {"email": email}
            ).scalar()

            if duplicate_check:
                raise HTTPException(
                    status_code=409,
                    detail="そのメールアドレスはすでに登録されています。"
                )

            # ユーザー登録
            conn.execute(
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

    except Exception as e:
        print(f"Error during user registration: {e}")
        raise HTTPException(status_code=500, detail=f"ユーザー登録中に予期せぬエラーが発生しました: {e}")


#ログイン画面の作成
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html",{"request": request})

#ログインの処理
@app.post("/login", response_class=HTMLResponse)
def login_system(request: Request, username_or_email  : str = Form(...), password: str = Form(...)):
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
            request.session["user_id"] = user.id
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
async def post_data(request: Request, user_id: str = Form(None), title: str = Form(...), place_name: str = Form(...), address: str = Form(), image_file: UploadFile = File(...), annotation: str = Form()):#これによりデータを受け取る
    try:
        with engine.begin() as conn:

            id_check = True
            while id_check:
                id = make_id(16)
                id_check = conn.execute(
                    text("SELECT EXISTS (SELECT 1 FROM posts WHERE id = :id)"),
                    {"id": id}
                ).scalar()

                id = "@" + id

            upload_file = await image_file.read()

            # Upload an image
            upload_result = cloudinary.uploader.upload(upload_file,public_id=id)
            print(upload_result["secure_url"])

            # Optimize delivery by resizing and applying auto-format and auto-quality
            optimize_url, _ = cloudinary_url("bachground", fetch_format="auto", quality="auto")
            print(optimize_url)

            # Transform the image: auto-crop to square aspect_ratio
            auto_crop_url, _ = cloudinary_url("bachground", width=500, height=500, crop="auto", gravity="auto")
            print(auto_crop_url)

            #投稿した画像のURLを取得
            file_URL = "https://res.cloudinary.com/djlgesfne/image/upload/" + image_file.filename

            #ユーザーIDを取得
            user_id = request.session.get("user_id")

            result = conn.execute(
                text("INSERT INTO posts (id, user_id, title, place_name, address, image_filename) VALUES (:id, :user_id, :title, :place_name, :address, :image_filename)"),
                {
                    "id": id,
                    "user_id": user_id,
                    "title": title,
                    "place_name": place_name,
                    "address": address,
                    "image_filename": file_URL,
                    "annotation": annotation
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
