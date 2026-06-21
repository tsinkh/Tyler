from fastapi import FastAPI
from pydantic import BaseModel

from backend.database import SessionLocal
from backend.models import File, Folder


app = FastAPI(
    title="Tyler API"
)

class FolderCreate(BaseModel):
    name: str
    parent_id: int | None = None

class MoveFile(BaseModel):
    folder_id: int


@app.get("/")
def root():

    return {
        "message":
        "Tyler is running"
    }


@app.get("/files")
def get_files():

    db = SessionLocal()

    files = (
        db.query(File)
        .all()
    )

    result = []

    for f in files:

        result.append(
            {
                "id": f.id,
                "name": f.file_name,
                "size": f.file_size,
                "telegram_message_id": f.telegram_message_id,
                "upload_time": f.upload_time,
                "mime_type": f.mime_type,
                "file_type": f.file_type,
                "has_thumbnail": f.has_thumbnail,
                "folder_id": f.folder_id
            }
        )

    db.close()

    return result


@app.get("/folders")
def get_folders():

    db = SessionLocal()

    folders = (
        db.query(Folder)
        .all()
    )

    result=[]

    for f in folders:

        result.append(
            {
                "id":f.id,
                "name":f.name,
                "parent_id":f.parent_id
            }
        )

    db.close()

    return result


@app.post("/folders")
def create_folder(
    folder: FolderCreate
):

    db = SessionLocal()

    new_folder = Folder(

        name=folder.name,

        parent_id=folder.parent_id

    )

    db.add(new_folder)

    db.commit()

    db.refresh(new_folder)

    db.close()

    return {
        "id": new_folder.id,
        "name": new_folder.name,
        "parent_id": new_folder.parent_id
    }


@app.put("/files/{file_id}/move")
def move_file(
    file_id:int,
    data:MoveFile
):

    db = SessionLocal()

    file = (
        db.query(File)
        .filter(
            File.id == file_id
        )
        .first()
    )

    if not file:

        db.close()

        return {
            "error":
            "file not found"
        }

    file.folder_id = data.folder_id

    db.commit()

    db.close()

    return {
        "message":
        "moved"
    }