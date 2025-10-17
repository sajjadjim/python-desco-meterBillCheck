#!/usr/bin/env python3
import os
import requests
from datetime import datetime

# Disable SSL warnings for now
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data(account_no: str, meter_no: str):
    URL = "https://prepaid.desco.org.bd/api/unified/customer/getBalance"
    params = {"accountNo": account_no, "meterNo": meter_no}
    try:
        res = requests.get(URL, params=params, verify=False, timeout=20)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def telegram_notify(token: str, chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=20)
        return {"ok": r.ok, "status": r.status_code, "text": r.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    account_no = os.getenv("ACCOUNT_NO")
    meter_no = os.getenv("METER_NO")

    print("⏱️ Run at:", datetime.utcnow().isoformat() + "Z")

    if not all([token, chat_id, account_no, meter_no]):
        print("❌ Missing env vars")
        return

    api_resp = fetch_data(account_no, meter_no)
    print("API response:", api_resp)

    if api_resp.get("data"):
        inner = api_resp["data"]
        balance = inner.get("balance", "Unknown")
        msg = f"💡 DESCO balance for account {account_no} (meter {meter_no}): {balance}\nChecked at {datetime.now().isoformat()}"
    else:
        code = api_resp.get("code")
        desc = api_resp.get("desc")
        msg = f"⚠️ DESCO API returned no data. code={code}, desc={desc}\nChecked at {datetime.now().isoformat()}"

    tg = telegram_notify(token, chat_id, msg)
    print("Telegram result:", tg)

if __name__ == "__main__":
    main()