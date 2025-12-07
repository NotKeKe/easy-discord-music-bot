from pathlib import Path
import sys
from dotenv import load_dotenv
import shutil
import os

MY_APP_NAME = "Easy Music Bot"

def get_app_data_path() -> Path:
    """取得一個跨平台的使用者應用程式資料儲存路徑"""
    home = Path.home()
    # 在 Windows 上會是 C:\Users\<user>\AppData\Roaming\MyApp
    # 在 Linux 上會是 /home/<user>/.config/MyApp
    if sys.platform == "win32":
        path = home / "AppData" / "Roaming" / MY_APP_NAME
    elif sys.platform == "linux":
        path = home / ".config" / MY_APP_NAME
    else: # macOS
        path = home / "Library" / "Application Support" / MY_APP_NAME

    path.mkdir(parents=True, exist_ok=True)
    return path

def resource_path(relative_path):
    """取得打包後的資源路徑"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path) # type: ignore
    return os.path.join(os.path.abspath("."), relative_path)

APP_DATA_PATH = get_app_data_path()

# get env
ENV_PATH = APP_DATA_PATH / ".env"
if not ENV_PATH.exists():
    shutil.copy(resource_path(".env.example"), ENV_PATH)
load_dotenv(APP_DATA_PATH / ".env")

DATA_PATH = APP_DATA_PATH / "data"
DATA_PATH.mkdir(exist_ok=True)

DB_PATH = DATA_PATH / "db"
DB_PATH.mkdir(exist_ok=True)

EMOJI_PATH = DATA_PATH / "emojis"
EMOJI_PATH.mkdir(exist_ok=True)

_owner_id = os.getenv("OWNER_ID", 0)
OWNER_ID = int(_owner_id if _owner_id and _owner_id != 'OWNER_ID' else 0)

FFMPEG_PATH = os.getenv('FFMPEG_PATH') or resource_path("assets/ffmpeg/ffmpeg.exe")