import requests
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime

# 监控配置
CHECK_IN = "06/20/2026"
CHECK_OUT = "06/21/2026"
PROPERTY = "YOSE_LODGE"  # Yosemite Valley Lodge
TARGET_EMAIL = "liqinrui1991@gmail.com"

def check_availability():
    url = "https://www.travelyosemite.com/api/availability"
    params = {
        "propertyCode": PROPERTY,
        "arrivalDate": CHECK_IN,
        "departureDate": CHECK_OUT,
        "adults": 1,
        "children": 0,
        "rooms": 1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
        return resp
    except Exception as e:
        print(f"Request error: {e}")
        return None

def check_page_availability():
    """直接抓取搜索结果页面判断是否有房"""
    url = "https://www.travelyosemite.com/lodging/yosemite-valley-lodge/"
    params = {
        "arrive": "06/20/2026",
        "depart": "06/21/2026",
        "adults": 1,
        "children": 0,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        content = resp.text.lower()
        print(f"Page status: {resp.status_code}, length: {len(content)}")

        # 判断有无空房的关键词
        has_room = any(kw in content for kw in [
            "add to cart", "book now", "available", "per night", "select room"
        ])
        no_room = any(kw in content for kw in [
            "no rooms available", "no availability", "sold out"
        ])

        print(f"Has room keywords: {has_room}, No room keywords: {no_room}")
        return has_room and not no_room, resp.text
    except Exception as e:
        print(f"Error: {e}")
        return False, ""

def send_email(subject, body):
    sender = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD")

    if not sender or not password:
        print("Email credentials not set, skipping email.")
        return

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = TARGET_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Email error: {e}")

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Checking Yosemite Valley Lodge availability for {CHECK_IN} - {CHECK_OUT}")

    available, page_content = check_page_availability()

    if available:
        print("🎉 ROOM AVAILABLE! Sending notification...")
        subject = "🏕️ Yosemite Valley Lodge 有房了！赶快预订！"
        body = f"""
        <h2>🎉 Yosemite Valley Lodge 出现空房！</h2>
        <p><strong>入住日期：</strong>{CHECK_IN}</p>
        <p><strong>退房日期：</strong>{CHECK_OUT}</p>
        <p><strong>检测时间：</strong>{now}</p>
        <p><a href="https://www.travelyosemite.com/lodging/yosemite-valley-lodge/?arrive=06/20/2026&depart=06/21/2026&adults=1&children=0" 
           style="background:#2d6a4f;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;">
           👉 立即预订
        </a></p>
        <p style="color:gray;font-size:12px;">此通知由 GitHub Actions 自动发送</p>
        """
        send_email(subject, body)
    else:
        print("No rooms available at this time.")

if __name__ == "__main__":
    main()
