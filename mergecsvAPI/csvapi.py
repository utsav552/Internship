from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import csv
import io
import random

app = FastAPI()

@app.post("/merge-csv/")
async def merge_csv(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    f1_text = await file1.read()
    f1_stream = io.StringIO(f1_text.decode())
    reader1 = csv.DictReader(f1_stream)

    data1 = {}
    for row in reader1:
        key = (row["epoch_time"], row["gmt_datetime"])
        data1[key] = {
            "epoch_time": row["epoch_time"],
            "gmt_datetime": row["gmt_datetime"],
            "Energy": row.get("Energy", "N/A")
        }

    f2_text = await file2.read()
    f2_stream = io.StringIO(f2_text.decode())
    reader2 = csv.DictReader(f2_stream)

    data2 = {}
    for row in reader2:
        key = (row["epoch_time"], row["gmt_datetime"])
        data2[key] = {"Power": row.get("Power", "N/A")}

    all_keys = set(data1.keys()) | set(data2.keys())
    merged_rows = []

    for key in sorted(all_keys):
        epoch, gmt = key

        energy = data1.get(key, {}).get("Energy", "N/A")
        power = data2.get(key, {}).get("Power", "N/A")

        merged_rows.append({
            "epoch_time": epoch,
            "gmt_datetime": gmt,
            "Energy": energy,
            "Power": power
        })

    random.shuffle(merged_rows)

    output_stream = io.StringIO()
    writer = csv.DictWriter(output_stream, fieldnames=["epoch_time", "gmt_datetime", "Energy", "Power"])
    writer.writeheader()
    writer.writerows(merged_rows)
    output_stream.seek(0)

    return StreamingResponse(
        iter([output_stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=merged.csv"}
    )

