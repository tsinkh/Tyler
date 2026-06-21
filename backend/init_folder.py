from backend.database import SessionLocal
from backend.models import Folder


db = SessionLocal()

root = Folder(
    name="Tyler",
    parent_id=None
)

db.add(root)

db.commit()

db.refresh(root)

uncategorized = Folder(
    name="未分类",
    parent_id=root.id
)

db.add(uncategorized)

db.commit()

db.close()

print("Folder initialized")