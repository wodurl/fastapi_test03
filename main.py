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

@app.get("/posts/new", response_class=HTMLResponse)
def postNewForm(request: Request):
    return templates.TemplateResponse(request=request, name="post/new-form.html")
    
@app.post("/posts/new")
def postNew(request: Request, writer: str = Form(...), title: str = Form(...), content: str = Form(...),
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
    return templates.TemplateResponse(
        request=request,
        name="post/alert.html",
        context={
            "msg":"글 정보를 추가했습니다",
            "url":"/posts"
        }
    )
    # return RedirectResponse("/posts", status_code=302)

@app.post("/posts/delete")
def postDelete(num: int = Form(...), db: Session = Depends(get_db)):
    # 삭제 SQL (RAW Query)
    query = text("""
        DELETE FROM post
        WHERE num = :num
    """)
    db.execute(query, {"num": num})
    db.commit()

    return RedirectResponse("/posts", status_code=302)

@app.get("/posts/edit/{num}")
def editForm(num: int, request: Request, db: Session = Depends(get_db)):
    # 수정할 글 정보를 읽어오기 위한 query 작성
    query = text("""SELECT num, writer, title, content, created_at
                    FROM post 
                    WHERE num=:num""")
    # PK를 이용해서 select하는 것이기 때문에 row는 1개다. 따라서 fetchone() 함수를 호출한다.
    row = db.execute(query, {"num": num}).fetchone()
    return templates.TemplateResponse(
        request=request,
        name="post/edit.html",
        context={
            "post":row
        }
    )

# 글 수정 반영 
@app.post("/posts/edit/{num}")
def edit(request: Request, num: int, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    query = text("""
        UPDATE post
        SET title=:title, content=:content
        WHERE num=:num
    """)
    db.execute(query, {"num":num, "title":title, "content":content})
    db.commit()
    return templates.TemplateResponse(
        request=request, 
        name="post/alert.html",
        context={
            "msg":"글 정보를 수정 했습니다!",
            "url":"/posts"
        }
    )