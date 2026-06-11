import requests
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime

CHECK_IN = "06/18/2026"
CHECK_OUT = "06/19/2026"
TARGET_EMAIL = "liqinrui1991@gmail.com"
LARK_WEBHOOK = os.environ.get("LARK_WEBHOOK")

def check_availability():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })

    # Step 1: 访问搜索页获取 Session
    search_url = "https://reservations.ahlsmsworld.com/Yosemite/Plan-Your-Trip/Accommodation-Search"
    r1 = session.get(search_url, timeout=20)
    print(f"Step 1 status: {r1.status_code}")

    # Step 2: 提交搜索表单
    form_data = {
        "Arrival": CHECK_IN,
        "Departure": CHECK_OUT,
        "Adults": "1",
        "Children": "0",
        "Rooms": "1",
        "PropCode": "000000",
    }
    r2 = session.post(search_url, data=form_data, timeout=20)
    print(f"Step 2 status: {r2.status_code}")

    # Step 3: 获取结果页
    results_url = "https://reservations.ahlsmsworld.com/Yosemite/Plan-Your-Trip/Accommodation-Search/Results"
    r3 = session.get(results_url, timeout=20)
    print(f"Step 3 status: {r3.status_code}, length:
