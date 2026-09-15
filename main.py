import uvicorn
from fastapi import FastAPI, Request, Form, Depends, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

# Твои модули
import database
import ml_model

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database.init_db()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- АУТЕНТИФИКАЦИЯ ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.username == username, database.User.password == password).first()
    if user:
        res = RedirectResponse(url="/", status_code=303)
        res.set_cookie(key="user_session", value=username)
        return res
    return RedirectResponse(url="/login", status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    new_user = database.User(username=username, password=password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
async def logout():
    res = RedirectResponse(url="/login", status_code=303)
    res.delete_cookie("user_session")
    return res

# --- ЗАЩИЩЕННЫЕ СТРАНИЦЫ ---

@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db), user_session: Optional[str] = Cookie(None)):
    if not user_session: return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(database.User).filter(database.User.username == user_session).first()
    if not user: return RedirectResponse(url="/login", status_code=303)

    active_tasks = db.query(database.Task).filter(database.Task.user_id == user.id, database.Task.status != 'done').all()
    all_tasks = db.query(database.Task).filter(database.Task.user_id == user.id).all()
    
    p_map = {'High': 0, 'Medium': 1, 'Low': 2}
    sorted_tasks = sorted(active_tasks, key=lambda x: (0 if x.status == 'doing' else 1, p_map.get(x.priority, 3)))
    
    return templates.TemplateResponse(
        request=request, name="dashboard.html", 
        context={"tasks": sorted_tasks, "all_tasks": all_tasks, "user": user_session}
    )

@app.get("/kanban", response_class=HTMLResponse)
async def kanban_page(request: Request, db: Session = Depends(get_db), user_session: Optional[str] = Cookie(None)):
    if not user_session: return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(database.User).filter(database.User.username == user_session).first()
    tasks = db.query(database.Task).filter(database.Task.user_id == user.id).all()
    
    return templates.TemplateResponse(
        request=request, name="kanban.html", context={"tasks": tasks}
    )

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, user_session: Optional[str] = Cookie(None)):
    if not user_session: return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="analytics.html")

@app.get("/focus", response_class=HTMLResponse)
async def focus_page(request: Request, db: Session = Depends(get_db), user_session: Optional[str] = Cookie(None)):
    if not user_session: return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(database.User).filter(database.User.username == user_session).first()
    doing_tasks = db.query(database.Task).filter(database.Task.user_id == user.id, database.Task.status == 'doing').all()
    
    return templates.TemplateResponse(
        request=request, name="focus.html", context={"tasks": doing_tasks}
    )

# --- ДЕЙСТВИЯ (API) ---

@app.post("/add_task")
async def add_task(
    title: str = Form(...), category: str = Form(...), 
    priority: Optional[str] = Form(None), time_est: Optional[float] = Form(None), 
    db: Session = Depends(get_db), user_session: Optional[str] = Cookie(None)
):
    if not user_session: return RedirectResponse(url="/login", status_code=303)
    user = db.query(database.User).filter(database.User.username == user_session).first()
    
    ai_priority, ai_time = ml_model.predict_task_params(title, category)
    new_task = database.Task(
        title=title, category=category, 
        priority=priority if priority and priority != "Auto" else ai_priority, 
        time_est=time_est if time_est is not None else ai_time,
        status="todo", user_id=user.id
    )
    db.add(new_task)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db), user_session: Optional[str] = Cookie(None)):
    if not user_session: return RedirectResponse(url="/login")
    user = db.query(database.User).filter(database.User.username == user_session).first()
    task = db.query(database.Task).filter(database.Task.id == task_id, database.Task.user_id == user.id).first()
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/move/{task_id}/{new_status}")
async def move_task(task_id: int, new_status: str, db: Session = Depends(get_db), user_session: Optional[str] = Cookie(None)):
    if not user_session: return RedirectResponse(url="/login")
    user = db.query(database.User).filter(database.User.username == user_session).first()
    task = db.query(database.Task).filter(database.Task.id == task_id, database.Task.user_id == user.id).first()
    if task:
        task.status = new_status
        db.commit()
    return RedirectResponse(url="/kanban", status_code=303)

@app.post("/update_time/{task_id}")
async def update_time(task_id: int, time_est: float = Form(...), db: Session = Depends(get_db), user_session: Optional[str] = Cookie(None)):
    if not user_session: return RedirectResponse(url="/login")
    user = db.query(database.User).filter(database.User.username == user_session).first()
    task = db.query(database.Task).filter(database.Task.id == task_id, database.Task.user_id == user.id).first()
    if task:
        task.time_est = time_est
        db.commit()
    return RedirectResponse(url="/kanban", status_code=303)

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db), user_session: Optional[str] = Cookie(None)):
    if not user_session: return {"error": "unauthorized"}
    user = db.query(database.User).filter(database.User.username == user_session).first()
    tasks = db.query(database.Task).filter(database.Task.user_id == user.id).all()
    
    total = len(tasks)
    counts = {"todo": 0, "doing": 0, "done": 0}
    categories = {}
    priorities = {"High": 0, "Medium": 0, "Low": 0}

    for t in tasks:
        s = t.status if t.status else "todo"
        counts[s] = counts.get(s, 0) + 1
        categories[t.category] = categories.get(t.category, 0) + 1
        if t.priority in priorities: priorities[t.priority] += 1

    score = int((counts['done'] / total * 100)) if total > 0 else 0
    return {
        "todo": counts['todo'], "doing": counts['doing'], "done": counts['done'],
        "score": score, "cat_labels": list(categories.keys()), "cat_values": list(categories.values()),
        "prio_labels": list(priorities.keys()), "prio_values": list(priorities.values())
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)