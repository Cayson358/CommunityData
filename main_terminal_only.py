import os
import asyncio
import requests
import random
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
import pytz
from dotenv import load_dotenv

# Load local .env (for testing locally)
load_dotenv()

# ======== Target Groups ==========
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

# ======== Time Formatter ==========
def get_my_time_str():
    tz = pytz.timezone("Asia/Kuala_Lumpur")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

# ======== Telegram Scraper ==========
async def collect_telegram():
    print("\n📡 Telegram Data:")

    api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        print("❌ TELEGRAM_API_ID or TELEGRAM_API_HASH not set")
        return

    async with TelegramClient('session', api_id, api_hash) as client:
        for ch in telegram_channels:
            try:
                entity = await client.get_entity(ch)
                full = await client(GetFullChannelRequest(entity))
                online = getattr(full.full_chat, 'online_count', 'N/A')
                total = getattr(full.full_chat, 'participants_count', 'N/A')
                print(f"{get_my_time_str()} | Telegram | {ch}: Online {online} / Total {total}")
            except Exception as e:
                print(f"⚠️ {ch} failed: {e}")

# ======== Discord Scraper ==========
def collect_discord():
    print("\n📡 Discord Data:")
    for name, code in discord_invites.items():
        url = f"https://discord.com/api/v9/invites/{code}?with_counts=true"
        try:
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            total = data.get("approximate_member_count", 'N/A')
            online = data.get("approximate_presence_count", 'N/A')
            print(f"{get_my_time_str()} | Discord | {name}: Online {online} / Total {total}")
        except Exception as e:
            print(f"⚠️ {name} failed: {e}")

# ======== Main Entry ==========
async def main():
    print(f"🕒 Started: {get_my_time_str()}")
    await collect_telegram()
    collect_discord()
    print(f"\n✅ Finished: {get_my_time_str()}")

if __name__ == "__main__":
    asyncio.run(main())
