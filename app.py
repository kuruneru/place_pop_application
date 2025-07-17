from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from sqlalchemy import create_engine, text
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
import os
import uuid
import shutil

#定義やインスタンス化
app = FastAPI()
db_url = os.getenv("DATABASE_URL")
templates = Jinja2Templates(directory="templates")
post_page = Jinja2Templates(directory="templates")
engine = create_engine(db_url)

#メインページが開かれたとき
@app.get("/")
def first(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "messages": "messages"})

#投稿用ページが開かれたとき
@app.get("/post")
def post_form(request: Request):
    return templates.TemplateResponse("post.html", {"request": request})

#投稿用ページから投稿についての処理が行われたとき
@app.post("/post")
def post_data(user_id: str = Form(...), title: str = Form(...), place_name: str = Form(...), address: str = Form(), ):
    #これによりファイルを受け取る
    image_file: UploadFile = File(...)
    #アップデートするファイルの保存場所
    UPLOAD_DIR = "templates/image_dir"
    #ファイルの拡張子の取得
    file_extension = os.path.splitext(image_file.filename)[1]
    #ファイルに一意味の名前をつける
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    #ファイルの名前を結合
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    #保存を試みる
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
            # shutil.copyfileobj: アップロードされたファイルの内容を効率的に保存
            # image_file.file: アップロードされたファイルの中身（ファイルオブジェクト）
            # buffer: 保存先のファイルオブジェクト
    #エラー発動の場合
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル保存中にエラーが発生しました:{e}")
    finally:
        image_file.file.close()

    with engine.begin() as conn:
        result = conn.execute(
            text("INSERT INTO posts (user_id, title, place_name, address) VALUES (:user_id, :title, :place_name, address)"),
            {
                "user_id": user_id,
                "title": title,
                "place_name": place_name,
                "address": address
            }
        )

    return {
        "success_message": "ファイルが正常にアップロードされました",
        "filename": image_file.filename,         # 元のファイル名
        "uploaded_filename": unique_filename,    # サーバーに保存されたファイル名
        "file_path": file_path                   # サーバー上のフルパス
    }