from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    BigInteger
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