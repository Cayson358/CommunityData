import os
import requests
import random
from datetime import datetime
import pytz

# ======== Discord Invites ==========
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
        # Slight delay to avoid rate limits
        time.sleep(random.uniform(1.0, 2.0))

# ======== Main Entry ==========
def main():
    print(f"🕒 Started: {get_my_time_str()}")
    collect_discord()
    print(f"\n✅ Finished: {get_my_time_str()}")

if __name__ == "__main__":
    main()
