from backend.database import SessionLocal
from backend.models import Folder


db = SessionLocal()

root = Folder(
    name="未分类",
    parent_id=None
)

db.add(root)

db.commit()

print(
    "Created folder:",
    root.id
)

db.close()