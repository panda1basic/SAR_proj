import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Переменная окружения DATABASE_URL не задана")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(title="Garazh API", version="1.0.0")

# Статика и шаблоны
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


class CarIn(BaseModel):
    brand: str = Field(..., min_length=1, max_length=64, description="Марка")
    model: str = Field(..., min_length=1, max_length=64, description="Модель")
    year: int = Field(..., ge=1950, le=2100, description="Год выпуска")
    plate: str | None = Field(default=None, max_length=16, description="Госномер (опционально)")


@app.on_event("startup")
def startup():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cars (
                id SERIAL PRIMARY KEY,
                brand VARCHAR(64) NOT NULL,
                model VARCHAR(64) NOT NULL,
                year INTEGER NOT NULL,
                plate VARCHAR(16),
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok", "service": "garazh", "ts": datetime.utcnow().isoformat() + "Z"}


@app.post("/cars")
def create_car(car: CarIn):
    with engine.begin() as conn:
        row = conn.execute(
            text("""
                INSERT INTO cars(brand, model, year, plate)
                VALUES (:brand, :model, :year, :plate)
                RETURNING id, brand, model, year, plate, created_at
            """),
            {
                "brand": car.brand.strip(),
                "model": car.model.strip(),
                "year": car.year,
                "plate": (car.plate.strip() if car.plate else None),
            },
        ).mappings().first()
    return dict(row)


@app.get("/cars")
def list_cars():
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, brand, model, year, plate, created_at FROM cars ORDER BY id DESC")
        ).mappings().all()
    return {"items": [dict(r) for r in rows]}


@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    with engine.begin() as conn:
        res = conn.execute(text("DELETE FROM cars WHERE id = :id"), {"id": car_id})
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="Машина не найдена")
    return {"ok": True, "message": "Машина удалена", "id": car_id}
