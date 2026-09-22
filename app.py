from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
from clean import run_pipeline

app = FastAPI(
    title="Climate Data Sanitizer API",
    description="An enterprise-grade microservice for automated climate time-series data cleaning.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "active", "service": "Climate Data Cleaning Pipeline API"}

@app.post("/clean-data/", summary="Upload corrupt CSV and download sanitized dataset")
async def clean_data_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    input_path = f"temp_{file.filename}"
    output_path = f"cleaned_{file.filename}"

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        run_pipeline(input_filepath=input_path, output_filepath=output_path)

        return FileResponse(
            path=output_path,
            filename=f"sanitized_{file.filename}",
            media_type="text/csv"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data Pipeline Error: {str(e)}")

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)