import os
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

# ======== Logging Function ==========
def log(msg):
    print(msg)
    with open("output.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ======== Discord Scraper ==========
def collect_discord():
    log("\n📡 Discord Data:")
    for name, code in discord_invites.items():
        url = f"https://discord.com/api/v9/invites/{code}?with_counts=true"
        try:
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            total = data.get("approximate_member_count", 'N/A')
            online = data.get("approximate_presence_count", 'N/A')
            log(f"{get_my_time_str()} | Discord | {name}: Online {online} / Total {total}")
        except Exception as e:
            log(f"⚠️ {name} failed: {e}")
        time.sleep(random.uniform(1.0, 2.0))  # light delay

# ======== Main Entry ==========
def main():
    with open("output.log", "a", encoding="utf-8") as f:
        f.write("\n\n📊 New Run — " + get_my_time_str() + "\n")
        f.write("===========================\n")

    log(f"🕒 Started: {get_my_time_str()}")
    collect_discord()
    log(f"\n✅ Finished: {get_my_time_str()}")

if __name__ == "__main__":
    main()
