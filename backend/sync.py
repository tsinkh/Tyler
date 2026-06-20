import asyncio

from telegram import client

from models import File
from database import SessionLocal


async def sync_channel(channel):

    db = SessionLocal()

    async for msg in client.iter_messages(channel):

        if not msg.file:
            continue

        exists = (
            db.query(File)
            .filter(
                File.telegram_message_id == msg.id
            )
            .first()
        )

        if exists:
            continue

        filename = (
            msg.file.name
            if msg.file.name
            else f"file_{msg.id}"
        )

        item = File(
            telegram_message_id=msg.id,
            file_name=filename,
            file_size=msg.file.size,
            upload_time=msg.date
        )

        db.add(item)

    db.commit()

    print("Sync completed")