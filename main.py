# main.py

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

# fasiapi 객체 생성
app = FastAPI()
# jinja2 템플릿 객체 생성 (templates 파일들이 어디에 있는지 알려야 한다.)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def indexs(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "fortuneToday":"이번달 안에 귀인을 만나"
        }
    )

# get 방식 /posts 요청 처리
@app.get("/posts", response_class=HTMLResponse)
def getPosts(request: Request, db: Session = Depends(get_db)):
    # DB에서 글 목록을 가져오기 위한 SQL문 준비
    query = text("""
        SELECT num, writer, title, content, created_at
        FROM post
        ORDER BY num DESC            
    """)
    # 글 목록을 얻어와
    result = db.execute(query)
    posts = result.fetchall()
    # 응답하기;
    return templates.TemplateResponse(
        request=request,
        name="post/list.html", # templates/post/list.html jinja2를 해석한 결과를 응답
        context={
            "post":posts
        }
    )

@app.get("/post/new", response_class=HTMLResponse)
def postNewForm(request: Request):
    return templates.TemplateResponse(request=request, name="post/new-form.html")
    
@app.post("/post/new")
def postNew(writer: str = Form(...), title: str = Form(...), content: str = Form(...),
            db: Session = Depends(get_db)):
    # DB에 저장할 SQL문 준비
    query = text("""
        INSERT INTO post
        (writer, title, content)
        VALUES(:writer, :title, :content)
    """)
    db.execute(query, {"writer":writer, "title":title, "content":content})
    db.commit()

    # 틀린 경로로 요청을 다시 하도록 리다이렉트 응답을 준다.
    return RedirectResponse("/posts", status_code=302)

@app.post("/post/delete")
def postDelete(num: int = Form(...), db: Session = Depends(get_db)):
    # 삭제 SQL (RAW Query)
    query = text("""
        DELETE FROM post
        WHERE num = :num
    """)
    db.execute(query, {"num": num})
    db.commit()

    return RedirectResponse("/posts", status_code=302)