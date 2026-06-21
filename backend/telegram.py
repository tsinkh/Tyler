from telethon import TelegramClient
from backend.config import API_ID, API_HASH, PROXY

client = TelegramClient(
    "tyler_session",
    API_ID,
    API_HASH,
    proxy=PROXY
)