from fastapi import FastAPI
from pydantic import BaseModel, RootModel
from typing import Dict, Any, List
from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, Float, String, select, update, insert, text
)
import os

app = FastAPI()
DATABASE_URL=os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
metadata = MetaData()
class AnalyticsItem(BaseModel):
    analytics_type: str
    asset_id: int
    data: Dict[str, Any]

class AnalyticsPayload(RootModel):
    root: List[AnalyticsItem]

def detect_type(value):
    if isinstance(value, int):
        return Integer
    elif isinstance(value, float):
        return Float
    else:
        return String(255)

def get_or_create_table(analytics_type: str, data: dict):
    table_name = analytics_type.lower()

    try:
        table = Table(table_name, metadata, autoload_with=engine)
    except Exception:
        columns = [Column("id", Integer, primary_key=True, autoincrement=True),
                   Column("asset_id", Integer, unique=True)]
        for key, value in data.items():
            if key != "asset_id":
                columns.append(Column(key, detect_type(value)))
        table = Table(table_name, metadata, *columns)
        metadata.create_all(engine)
        return table

    existing_columns = table.columns.keys()
    new_columns = []
    for key, value in data.items():
        if key != "asset_id" and key not in existing_columns:
            col_type = detect_type(value)
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {key} {col_type().compile(dialect=engine.dialect)}'))
            new_columns.append(key)

    if new_columns:
        table = Table(table_name, metadata, autoload_with=engine)

    return table

@app.post("/analytics")
async def store_analytics(payload: AnalyticsPayload):
    rows = payload.root

    with engine.begin() as conn:
        for item in rows:
            table_data = {"asset_id": item.asset_id}
            table_data.update(item.data)

            table = get_or_create_table(item.analytics_type, table_data)

            stmt = select(table).where(table.c.asset_id == item.asset_id)
            result = conn.execute(stmt).first()
            if result:
                upd = update(table).where(table.c.asset_id == item.asset_id).values(**table_data)
                conn.execute(upd)
            else:
                ins = insert(table).values(**table_data)
                conn.execute(ins)

    return {"message": "Analytics updated successfully"}

@app.get("/")
def root():
    return {"status": "running", "endpoint": "/analytics"}
