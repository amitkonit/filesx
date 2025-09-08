import os, sqlite3, zipfile, asyncio
from pyrogram import Client

api_id = int(os.environ["TG_API_ID"])
api_hash = os.environ["TG_API_HASH"]
bot_token = os.environ["TG_BOT_TOKEN"]
chat_id = int(os.environ["TG_CHAT_ID"])

BACKUP_ZIP = "browsers_backup.zip"
STORE_DB = "store.db"

BROWSER_PATHS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"),
    os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
]

async def download_files(app: Client):
    async for m in app.get_chat_history(chat_id, limit=20):
        if m.document:
            if m.document.file_name == STORE_DB:
                await app.download_media(m, file_name=STORE_DB)
            elif m.document.file_name == BACKUP_ZIP:
                await app.download_media(m, file_name=BACKUP_ZIP)

def restore_data():
    if not os.path.exists(BACKUP_ZIP):
        return
    with zipfile.ZipFile(BACKUP_ZIP, 'r') as zipf:
        zipf.extractall(os.path.expandvars(r"%LOCALAPPDATA%"))

async def main():
    async with Client("bot", api_id, api_hash, bot_token=bot_token) as app:
        await download_files(app)

    if os.path.exists(STORE_DB):
        conn = sqlite3.connect(STORE_DB)
        cur = conn.cursor()
        cur.execute("SELECT backup_file FROM runs ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        if row:
            restore_data()

if __name__ == "__main__":
    asyncio.run(main())
