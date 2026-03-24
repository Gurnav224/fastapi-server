from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session

app = FastAPI()

DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TodoDB(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False, default="")
    done = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

class TodoCreate(BaseModel):
    title: str
    description: str = ""

class TodoRead(BaseModel):
    id: int
    title: str
    description: str = ""
    done: bool = False

    model_config = {"from_attributes": True}

class TodoUpdate(BaseModel):
    title: str
    description: str = ""

class TodoDone(BaseModel):
    done: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["health"])
def read_root():
    return {"message": "Hello from FastAPI 🚀"}

@app.get("/todos", response_model=List[TodoRead], tags=["todos"])
def list_todos(db: Session = Depends(get_db)):
    return db.query(TodoDB).all()

@app.post("/todos", response_model=TodoRead, status_code=201, tags=["todos"])
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoDB(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/{todo_id}", response_model=TodoRead, tags=["todos"])
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(TodoDB, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoRead, tags=["todos"])
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.get(TodoDB, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.title = todo.title
    db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.patch("/todos/{todo_id}/done", response_model=TodoRead, tags=["todos"])
def mark_done(todo_id: int, payload: TodoDone, db: Session = Depends(get_db)):
    db_todo = db.get(TodoDB, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.done = payload.done
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", status_code=204, tags=["todos"])
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.get(TodoDB, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return None


