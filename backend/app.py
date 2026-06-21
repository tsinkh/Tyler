from fastapi import FastAPI

from backend.database import SessionLocal
from backend.models import File


app = FastAPI(
    title="Tyler API"
)



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

                "name":
                f.file_name,

                "size":
                f.file_size,

                "telegram_message_id":
                f.telegram_message_id,

                "upload_time":
                f.upload_time
            }
        )


    db.close()


    return result