
from fastapi import FastAPI, Depends, HTTPException, UploadFile, Form, File, Request
import models, fr_helper
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")

class User(BaseModel):
    id: int
    name: str
    email: str

    @classmethod
    def as_form(
        cls,
        id: int = Form(...),
        name: str = Form(...),
        email: str = Form(...)
    ):
        return cls(id=id, name=name, email=email)

def create_user(db: Session, user: User, face_encoding: str):
    db_user = models.User(id=user.id, name=user.name, email=user.email, face_encoding=face_encoding)
    db.add(db_user)
    db.commit()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, limit: 10, offset):
    return db.query(models.User).offset(offset).limit(limit).all()

def update_user(db: Session, user: User):
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    for var, value in vars(user).items():
        setattr(db_user, var, value)
    db.commit()
    db.refresh(db_user)

def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "created": False})

@app.post("/register")
async def register(request: Request, user: User = Depends(User.as_form), file: UploadFile = File(...), db: Session = Depends(get_db)):
    face_encoding = fr_helper.get_face_encodings(file.file)
    create_user(db=db, user=user, face_encoding=face_encoding)
    return templates.TemplateResponse("register.html", {"request": request, "created": True})


@app.get("/recognize")
def recognize(request: Request):
    return templates.TemplateResponse("recognize.html", {"request": request, "get": True})

@app.post("/recognize")
async def recognize(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    face_encoding = fr_helper.get_face_encodings(file.file)
    offset = 0
    limit = 5
    while True:
        users = get_users(db, limit, offset)
        if users == []:
            break
        for user in users:
            result = fr_helper.compare(user.face_encoding, face_encoding)
            if result[0]:
                return templates.TemplateResponse("recognize.html", {"request": request, "user": user, "get": False})
        offset = offset + 5
    return templates.TemplateResponse("recognize.html", {"request": request, "get": False})

@app.post("/delete/{user_id}")
def delete(request: Request, user_id: int, db: Session = Depends(get_db)):
    delete_user(db=db, user_id=user_id)
    return templates.TemplateResponse("index.html", {"request": request, "message": "User deleted!!!"})

@app.post("/get_update/{user_id}")
def get_update(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    return templates.TemplateResponse("update.html", {"request": request, "user": user})

@app.post("/get_update/update/{user_id}")
def update(request: Request, user: User = Depends(User.as_form), db: Session = Depends(get_db)):
    update_user(db=db, user=user)
    return templates.TemplateResponse("update.html", {"request": request, "message": "User updated!!!"})