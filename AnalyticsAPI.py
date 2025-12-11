from fastapi import FastAPI
from pydantic import BaseModel, RootModel
from typing import Dict, Any, List
from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, Float, String, BigInteger, ForeignKey,
     insert, text
)
import os
import time

app = FastAPI()

DATABASE_URL = os.getenv("Db_url")
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


analytics_main = Table(
    "analytics_main",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("asset_id", Integer, nullable=False),
    Column("analytics_type", String(255), nullable=False),
    Column("epoch_time", BigInteger, nullable=False),
)

metadata.create_all(engine)

def get_or_create_child_table(analytics_type: str, data: dict):
    table_name = f"{analytics_type.lower()}_data"

    try:
        table = Table(table_name, metadata, autoload_with=engine)
    except Exception:
        columns = [
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("analytics_id", Integer, ForeignKey("analytics_main.id", ondelete="CASCADE")),
        ]
        for key, value in data.items():
            columns.append(Column(key, detect_type(value)))

        table = Table(table_name, metadata, *columns)
        metadata.create_all(engine)
        return table

    existing_columns = table.columns.keys()
    for key, value in data.items():
        if key not in existing_columns:
            col_type = detect_type(value)
            with engine.begin() as conn:
                conn.execute(
                    text(
                        f'ALTER TABLE {table_name} ADD COLUMN {key} {col_type().compile(dialect=engine.dialect)}'
                    )
                )
            table = Table(table_name, metadata, autoload_with=engine)

    return table


@app.post("/analytics")
async def store_analytics(payload: AnalyticsPayload):
    rows = payload.root

    with engine.begin() as conn:
        for item in rows:
            current_time = int(time.time())

            ins_main = insert(analytics_main).values(
                asset_id=item.asset_id,
                analytics_type=item.analytics_type,
                epoch_time=current_time,
            )
            res = conn.execute(ins_main)
            analytics_id = res.inserted_primary_key[0]

            child_table = get_or_create_child_table(item.analytics_type, item.data)
            data_with_fk = {"analytics_id": analytics_id}
            data_with_fk.update(item.data)

            ins_child = insert(child_table).values(**data_with_fk)
            conn.execute(ins_child)

    return {"message": "Analytics stored successfully (normalized + dynamic)"}


@app.get("/")
def root():
    return {"status": "running", "endpoint": "/analytics"}
