from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    BigInteger,
    Boolean
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)

    telegram_message_id = Column(BigInteger, unique=True)

    file_name = Column(String)

    file_size = Column(BigInteger)

    upload_time = Column(DateTime)

    mime_type = Column(String)

    file_type = Column(String)

    has_thumbnail = Column(Boolean, default=False)