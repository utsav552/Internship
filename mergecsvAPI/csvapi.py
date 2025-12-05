from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import csv
import io

app = FastAPI()

def row_generator(file1, file2):
    reader1 = csv.DictReader(io.TextIOWrapper(file1, encoding="utf-8"))
    reader2 = csv.DictReader(io.TextIOWrapper(file2, encoding="utf-8"))

    row1 = next(reader1, None)
    row2 = next(reader2, None)

    while row1 or row2:
        if row1 and row2:
            key1 = (row1["epoch_time"], row1["gmt_datetime"])
            key2 = (row2["epoch_time"], row2["gmt_datetime"])

            if key1 == key2:
                yield {
                    "epoch_time": row1["epoch_time"],
                    "gmt_datetime": row1["gmt_datetime"],
                    "Energy": row1.get("Energy", "N/A"),
                    "Power": row2.get("Power", "N/A"),
                }
                row1 = next(reader1, None)
                row2 = next(reader2, None)

            elif key1 < key2:
                yield {
                    "epoch_time": row1["epoch_time"],
                    "gmt_datetime": row1["gmt_datetime"],
                    "Energy": row1.get("Energy", "N/A"),
                    "Power": "N/A"
                }
                row1 = next(reader1, None)

            else:
                yield {
                    "epoch_time": row2["epoch_time"],
                    "gmt_datetime": row2["gmt_datetime"],
                    "Energy": "N/A",
                    "Power": row2.get("Power", "N/A")
                }
                row2 = next(reader2, None)

        elif row1:
            yield {
                "epoch_time": row1["epoch_time"],
                "gmt_datetime": row1["gmt_datetime"],
                "Energy": row1.get("Energy", "N/A"),
                "Power": "N/A"
            }
            row1 = next(reader1, None)

        elif row2:
            yield {
                "epoch_time": row2["epoch_time"],
                "gmt_datetime": row2["gmt_datetime"],
                "Energy": "N/A",
                "Power": row2.get("Power", "N/A")
            }
            row2 = next(reader2, None)

@app.post("/merge-csv/")
async def merge_csv(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    def generate():
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["epoch_time", "gmt_datetime", "Energy", "Power"])
        writer.writeheader()
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for row in row_generator(file1.file, file2.file):
            writer.writerow(row)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=merged.csv"}
    )
