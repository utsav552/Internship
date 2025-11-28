from fastapi import FastAPI, UploadFile, File
import pandas as pd
from fastapi.responses import StreamingResponse
import io

app = FastAPI()

@app.post("/merge-csv/")
async def merge_csv(
    file1: UploadFile = File(...), 
    file2: UploadFile = File(...)
    ):

    df1 = pd.read_csv(file1.file)
    df2 = pd.read_csv(file2.file)

    merged_df = pd.merge(df1, df2, on=["epoch_time", "gmt_datetime"], how="outer").fillna("N/a")

    stream = io.StringIO()
    merged_df.to_csv(stream, index=False)
    stream.seek(0)

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=merged.csv"
        }
    )

