from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class TodoItem(BaseModel):
    id: int
    title: str
    description: str = ""
    done: bool = False

class TodoCreate(BaseModel):
    title: str
    description: str = ""

# In-memory store
todos: List[TodoItem] = []
next_id = 1

@app.get("/", tags=["health"])
def read_root():
    return {"message": "Hello from FastAPI 🚀"}

@app.get("/todos", response_model=List[TodoItem], tags=["todos"])
def list_todos():
    return todos

@app.post("/todos", response_model=TodoItem, status_code=201, tags=["todos"])
def create_todo(todo: TodoCreate):
    global next_id
    item = TodoItem(id=next_id, title=todo.title, description=todo.description)
    todos.append(item)
    next_id += 1
    return item

@app.get("/todos/{todo_id}", response_model=TodoItem, tags=["todos"])
def get_todo(todo_id: int):
    for item in todos:
        if item.id == todo_id:
            return item
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/todos/{todo_id}", response_model=TodoItem, tags=["todos"])
def update_todo(todo_id: int, todo: TodoCreate):
    for idx, item in enumerate(todos):
        if item.id == todo_id:
            updated = item.copy(update={"title": todo.title, "description": todo.description})
            todos[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Todo not found")

@app.patch("/todos/{todo_id}/done", response_model=TodoItem, tags=["todos"])
def mark_done(todo_id: int, done: bool):
    for idx, item in enumerate(todos):
        if item.id == todo_id:
            updated = item.copy(update={"done": done})
            todos[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}", status_code=204, tags=["todos"])
def delete_todo(todo_id: int):
    for idx, item in enumerate(todos):
        if item.id == todo_id:
            todos.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Todo not found")


