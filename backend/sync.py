import asyncio

from telegram import client
from config import CHANNEL_ID

from database import SessionLocal
from models import File


async def sync():
    await client.start()

    db = SessionLocal()
    channel = await client.get_entity(CHANNEL_ID)

    async for msg in client.iter_messages(channel):

        if not msg.document:
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
            msg.document.name
            if msg.document.name
            else f"unknown_{msg.id}"
        )

        file = File(
            telegram_message_id=msg.id,
            file_name=filename,
            file_size=msg.document.size,
            upload_time=msg.date
        )

        db.add(file)
        print(
            "Added:",
            filename
        )

    db.commit()

    db.close()
asyncio.run(sync())telegram_message_ids = set()