import requests
import random
import time
from datetime import datetime
import pytz

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

def collect_discord():
    print(f"\nDiscord Data — {get_my_time_str()}")
    for name, code in discord_invites.items():
        url = f"https://discord.com/api/v9/invites/{code}?with_counts=true"
        try:
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            total = data.get("approximate_member_count", 'N/A')
            online = data.get("approximate_presence_count", 'N/A')
            print(f"{name}: Online {online} / Total {total}")
        except Exception as e:
            print(f"{name} failed: {e}")
        time.sleep(random.uniform(1.0, 2.0))

if __name__ == "__main__":
    collect_discord()

