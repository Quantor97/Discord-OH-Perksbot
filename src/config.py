import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PERKS_URL = os.getenv("PERKS_EXCEL_URL")
MAX_PERKS = 10

if __name__ == '__main__':
    print(DISCORD_TOKEN)
    print(PERKS_URL)