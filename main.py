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

telegram_channels = [
    '@OKXGroup_CN',
    '@BinanceChinese',
    '@binanceexchange'
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

async def collect_telegram(service):
    print("📡 抓取 Telegram 数据...")
    load_dotenv()
    api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_id or not api_hash:
        print("❌ TELEGRAM_API_ID 或 API_HASH 未设置")
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
                print(f"✅ Telegram | {ch}: 在线 {online} / 总数 {total}")
                append_to_sheet(service, row)
            except Exception as e:
                print(f"❌ 抓取 {ch} 失败: {e}")

def collect_discord(service):
    print("📡 抓取 Discord 数据...")
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
            print(f"✅ Discord | {name}: 在线 {online} / 总数 {total}")
            append_to_sheet(service, row)
        except Exception as e:
            print(f"❌ 抓取 {name} 失败: {e}")
        time.sleep(random.uniform(1.0, 2.0))

# ======== 主循环：从 00:00 开始，每 3 小时执行一次 ==========
async def run_every_3_hours():
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    print("🔄 定时任务开始（每 3 小时运行）")

    while True:
        now = datetime.now(pytz.timezone("Asia/Kuala_Lumpur"))
        if count_today_entries(service) >= 8:
            print("⚠️ 今天已达到 8 次写入限制，暂停采集。")
        else:
            print(f"\n⏰ 开始采集时间：{now.strftime('%Y-%m-%d %H:%M:%S')}")
            await collect_telegram(service)
            collect_discord(service)

        # 计算下一个整点（每 3 小时）的时间
        next_hour = (now.hour // 3 + 1) * 3
        if next_hour >= 24:
            next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            next_run = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)

        wait_seconds = (next_run - now).total_seconds()
        print(f"⏳ 等待 {round(wait_seconds / 60)} 分钟至下一次采集...\n")
        await asyncio.sleep(wait_seconds)

# ======== 程序入口 ==========
if __name__ == "__main__":
    asyncio.run(run_every_3_hours())
