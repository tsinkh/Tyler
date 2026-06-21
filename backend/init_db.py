from backend.models import Base
from backend.database import engine

Base.metadata.create_all(engine)

print("Database initialized")