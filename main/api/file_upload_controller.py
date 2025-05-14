from fastapi import APIRouter, UploadFile, File
import os

uploadRouter = APIRouter()

#TARGET_DIR = r"C:\Users\nivii\programming\CS degree\year 3\WorkShop\lastYearProject\main\data"
TARGET_DIR = r"C:\Users\Lior\Desktop\Lior\year3\project\LastYearProject\main\data"

@uploadRouter.post("/upload")
async def upload_files(
        schema_file: UploadFile = File(...),
        data_file: UploadFile = File(...)
):
    os.makedirs(TARGET_DIR, exist_ok=True)

    schema_filename = schema_file.filename
    data_filename = data_file.filename

    schema_path = os.path.join(TARGET_DIR, schema_filename)
    data_path = os.path.join(TARGET_DIR, data_filename)

    with open(schema_path, "wb") as f:
        f.write(await schema_file.read())

    with open(data_path, "wb") as f:
        f.write(await data_file.read())

    print(f"✅ Saved {schema_filename} at {schema_path}")
    print(f"✅ Saved {data_filename} at {data_path}")

    return {
        "message": "Files uploaded successfully",
        "schema_file": schema_filename,
        "data_file": data_filename
    }
