import os
from dotenv import load_dotenv

load_dotenv()


FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "cli_xxxxxxx")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your_feishu_app_secret")

