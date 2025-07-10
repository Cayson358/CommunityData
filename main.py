import os
import asyncio
import requests
import time
import random
from datetime import datetime, timedelta
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pytz
from dotenv import load_dotenv

# ======== Google Sheet 设置 ==========
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1-VPerABWZChUzMEfPAALaPOYfe-oTLF1SEAWk8APwsY'
SHEET_NAME = 'community_data'

# ======== 群组设置 ==========
telegram_channels = [
    '@OKXGroup_CN',
    '@BinanceChinese',
    '@binanceexchange',
    '@OKXOfficial_English',
    '@OKXWalletEN_Official',
    '@OKXWallet_CN',
    '@Bitget_Wallet'
]

discord_invites = {
    "BINANCE": "binanceofficial",
    "BINANCE_CN": "bnb",
    "BYBIT": "bybit",
    "KUCOIN": "kucoinofficialserver",
    "OKX": "okx",
    "OKX_CN": "hkCGKbbbqf",
    "Bitget": "bitget"
}

# ======== 时间函数 ==========
def get_my_time_str():
    tz = pytz.timezone("Asia/Kuala_Lumpur")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def count_today_entries(service):
    today = datetime.now(pytz.timezone("Asia/Kuala_Lumpur")).strftime('%Y-%m-%d')
    range_name = f'{SHEET_NAME}!A2:E'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    return sum(1 for row in values if len(row) >= 5 and row[4].startswith(today))

def append_to_sheet(service, row):
    body = {'values': [row]}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A1',
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

# ======== Telegram 抓取函数 ==========
async def collect_telegram(service):
    print("Fetching Telegram data...")
    load_dotenv()
    api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_id or not api_hash:
        print("TELEGRAM_API_ID or API_HASH not set")
        return

    async with TelegramClient('session', api_id, api_hash) as client:
        for ch in telegram_channels:
            try:
                entity = await client.get_entity(ch)
                full = await client(GetFullChannelRequest(entity))
                online = getattr(full.full_chat, 'online_count', 'N/A')
                total = getattr(full.full_chat, 'participants_count', 'N/A')
                timestamp = get_my_time_str()
                row = ['telegram', ch, online, total, timestamp]
                print(f"Telegram | {ch}: Online {online} / Total {total}")
                append_to_sheet(service, row)
            except Exception as e:
                print(f"Failed to fetch {ch}: {e}")

# ======== Discord 抓取函数 ==========
def collect_discord(service):
    print("Fetching Discord data...")
    for name, code in discord_invites.items():
        url = f"https://discord.com/api/v9/invites/{code}?with_counts=true"
        try:
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            total = data.get("approximate_member_count", 'N/A')
            online = data.get("approximate_presence_count", 'N/A')
            timestamp = get_my_time_str()
            row = ['discord', name, online, total, timestamp]
            print(f"Discord | {name}: Online {online} / Total {total}")
            append_to_sheet(service, row)
        except Exception as e:
            print(f"Failed to fetch {name}: {e}")
        time.sleep(random.uniform(1.0, 2.0))

# ======== 主循环：每小时执行一次 ==========
async def run_every_hour():
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    print("Scheduled task started (every hour)")

    while True:
        now = datetime.now(pytz.timezone("Asia/Kuala_Lumpur"))
        if count_today_entries(service) >= 24:
            print("Reached daily write limit (24 entries), pausing collection.")
        else:
            print(f"\nStart collection at: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            await collect_telegram(service)
            collect_discord(service)

        next_run = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        wait_seconds = (next_run - now).total_seconds()
        print(f"Waiting {round(wait_seconds / 60)} minutes until next run...\n")
        await asyncio.sleep(wait_seconds)

# ======== 程序入口 ==========
if __name__ == "__main__":
    asyncio.run(run_every_hour())
