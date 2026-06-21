from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
from urllib.parse import quote

from backend.database import SessionLocal
from backend.models import File, Folder
from backend.telegram import client
from backend.config import CHANNEL_ID


app = FastAPI(
    title="Tyler API"
)

def build_content_disposition(filename: str) -> str:

    ascii_filename = (
        filename.encode("ascii", "ignore").decode("ascii").strip()
        or "download"
    )

    return (
        f'attachment; filename="{ascii_filename}"; '
        f"filename*=UTF-8''{quote(filename)}"
    )

@app.on_event("startup")
async def startup_event():

    await client.start()

class FolderCreate(BaseModel):
    name: str
    parent_id: int | None = None

class MoveFile(BaseModel):
    folder_id: int

def build_tree(folder, db):

    children = (
        db.query(Folder)
        .filter(
            Folder.parent_id == folder.id
        )
        .all()
    )

    files = (
        db.query(File)
        .filter(
            File.folder_id == folder.id
        )
        .all()
    )

    node = {
        "id": folder.id,
        "name": folder.name,
        "type": "folder",
        "children": [],
        "files": []
    }

    for child in children:

        node["children"].append(
            build_tree(
                child,
                db
            )
        )

    for file in files:

        node["files"].append(
            {
                "id": file.id,
                "name": file.file_name,
                "size": file.file_size,
                "mime_type": file.mime_type,
                "type": "file"
            }
        )

    return node


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


@app.get("/folders/{folder_id}/content")
def get_folder_content(folder_id: int):

    db = SessionLocal()
    folder = (
        db.query(Folder)
        .filter(
            Folder.id == folder_id
        )
        .first()
    )

    if not folder:

        db.close()

        return {
            "error": "folder not found"
        }

    folders = (
        db.query(Folder)
        .filter(
            Folder.parent_id == folder_id
        )
        .all()
    )

    files = (
        db.query(File)
        .filter(
            File.folder_id == folder_id
        )
        .all()
    )

    result = {
        "folder": {
            "id": folder.id,
            "name": folder.name
        },
        "folders": [],
        "files": []
    }

    for f in folders:

        result["folders"].append(
            {
                "id": f.id,
                "name": f.name
            }
        )

    for file in files:

        result["files"].append(
            {
                "id": file.id,
                "name": file.file_name,
                "size": file.file_size,
                "mime_type": file.mime_type,
                "file_type": file.file_type
            }
        )

    db.close()

    return result


@app.get("/root")
def get_root():

    db = SessionLocal()

    root = (
        db.query(Folder)
        .filter(
            Folder.parent_id == None
        )
        .first()
    )

    db.close()

    return {
        "id": root.id,
        "name": root.name
    }


@app.get("/tree")
def get_tree():

    db = SessionLocal()

    root = (
        db.query(Folder)
        .filter(
            Folder.parent_id == None
        )
        .first()
    )

    if not root:

        db.close()

        return {
            "error":
            "no root folder"
        }

    tree = build_tree(
        root,
        db
    )

    db.close()

    return tree


@app.get("/files/{file_id}")
def get_file(file_id:int):

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

    result = {
        "id": file.id,
        "name": file.file_name,
        "size": file.file_size,
        "mime_type": file.mime_type,
        "file_type": file.file_type,
        "telegram_message_id": file.telegram_message_id,
        "upload_time": file.upload_time
    }

    db.close()

    return result


@app.get("/files/{file_id}/download")
async def download_file(file_id:int):

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

    message = await client.get_messages(
        CHANNEL_ID,
        ids=file.telegram_message_id
    )

    if not message:

        db.close()

        return {
            "error":
            "telegram file not found"
        }

    async def file_stream():

        buffer = io.BytesIO()

        await client.download_media(
            message,
            file=buffer
        )

        buffer.seek(0)

        while chunk := buffer.read(1024*1024):

            yield chunk

    db.close()

    return StreamingResponse(
        file_stream(),
        media_type=file.mime_type,
        headers={
            "Content-Disposition":
            build_content_disposition(file.file_name)
        }
    )