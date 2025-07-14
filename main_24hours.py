import requests
import random
import time
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
    print(f"\n Discord Data — {get_my_time_str()}")
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

# ======== Main Loop ==========
def main():
    for i in range(23):  # Repeat 23 times
        print(f"\n=== Cycle {i+1}/23 started ===")
        collect_discord()
        if i < 22:
            print("Waiting 1 hour until next cycle...\n")
            time.sleep(3600)  # 1 hour
    print(f"\n All 23 cycles completed at {get_my_time_str()}")

if __name__ == "__main__":
    main()
