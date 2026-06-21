import asyncio

from backend.telegram import client
from backend.config import CHANNEL_ID

from backend.database import SessionLocal
from backend.models import File


async def sync():
    telegram_message_ids = set()
    await client.start()

    db = SessionLocal()
    channel = await client.get_entity(CHANNEL_ID)

    async for msg in client.iter_messages(channel):

        if not msg.file:
            continue

        telegram_message_ids.add(msg.id)

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
            else f"unknown_{msg.id}"
        )

        file = File(
            telegram_message_id=msg.id,
            file_name=filename,
            file_size=msg.file.size,
            upload_time=msg.date
        )

        db.add(file)
        print(
            "Added:",
            filename
        )

    db_files = db.query(File).all()

    for f in db_files:

        if f.telegram_message_id in telegram_message_ids:
            continue

        print(
            "Removed:",
            f.file_name
        )

        db.delete(f)

    db.commit()

    db.close()

asyncio.run(sync())