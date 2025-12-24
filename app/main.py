import os
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(title="SAR API", version="1.0.0")

# раздача /static/*
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# главная страница
@app.get("/", include_in_schema=False)
def root():
    return FileResponse("app/templates/index.html")

class NoteIn(BaseModel):
    text: str

@app.on_event("startup")
def startup():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL
            );
        """))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/notes")
def create_note(note: NoteIn):
    with engine.begin() as conn:
        row = conn.execute(
            text("INSERT INTO notes(text) VALUES (:t) RETURNING id, text"),
            {"t": note.text},
        ).mappings().first()
    return dict(row)

@app.get("/notes")
def list_notes():
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, text FROM notes ORDER BY id")).mappings().all()
    return {"items": [dict(r) for r in rows]}
