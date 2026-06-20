from fastapi import FastAPI

from database import SessionLocal
from models import File

app = FastAPI()


@app.get("/files")
def list_files():

    db = SessionLocal()

    files = db.query(File).all()

    return [
        {
            "id": f.id,
            "name": f.file_name,
            "size": f.file_size
        }
        for f in files
    ]