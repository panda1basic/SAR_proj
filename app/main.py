import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://sar:sar@localhost:5432/sar")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(title="SAR Demo (Satisfactory)", version="1.0.0")

# static + templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def init_db():
    # Простая инициализация таблицы (для демо-работы достаточно)
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            value INT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """))

@app.on_event("startup")
def on_startup():
    init_db()


class ItemCreate(BaseModel):
    name: str
    value: int


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/items")
def create_item(payload: ItemCreate):
    with engine.begin() as conn:
        row = conn.execute(
            text("INSERT INTO items (name, value) VALUES (:name, :value) RETURNING id, name, value, created_at"),
            {"name": payload.name, "value": payload.value},
        ).mappings().first()
    return {
        "id": row["id"],
        "name": row["name"],
        "value": row["value"],
        "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
    }


@app.get("/api/items")
def list_items():
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, name, value, created_at FROM items ORDER BY id DESC LIMIT 100")
        ).mappings().all()

    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "name": r["name"],
            "value": r["value"],
            "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
        })
    return items


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT id, name, value, created_at FROM items WHERE id=:id"),
            {"id": item_id},
        ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Item not found")

    return {
        "id": row["id"],
        "name": row["name"],
        "value": row["value"],
        "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
    }
