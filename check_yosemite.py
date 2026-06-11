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
    # 直接调用 Aramark 的房间搜索 API
    url = "https://www.travelyosemite.com/api/2.0/redis/rooms/search"
    params = {
        "propertyCode": "YRLODGE",
        "arrivalDate": CHECK_IN,
        "departureDate": CHECK_OUT,
        "adults": "1",
        "children": "0",
        "numRooms": "1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.travelyosemite.com/lodging/yosemite-valley-lodge/",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        print(f"API status: {resp.status_code}")
        print(f"API response: {resp.text[:1000]}")
        
        if resp.status_code == 200:
            data = resp.json()
            rooms = data.get("rooms", data.get("results", data.get("data", [])))
            print(f"Rooms found: {len(rooms) if isinstance(rooms, list) else rooms}")
            return len(rooms) > 0 if isinstance(rooms, list) else False
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def send_lark(message):
    if not LARK_WEBHOOK:
        print("Lark webhook not set")
        return
    try:
        resp = requests.post(LARK_WEBHOOK, json={
            "msg_type": "text",
            "content": {"text": message}
        }, timeout=10)
        print(f"Lark sent: {resp.status_code}, {resp.text}")
    except Exception as e:
        print(f"Lark error: {e}")

def send_email(subject, body):
    sender = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender or not password:
        return
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = TARGET_EMAIL
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Email sent!")
    except Exception as e:
        print(f"Email error: {e}")

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Checking Yosemite Valley Lodge for {CHECK_IN} - {CHECK_OUT}")

    available = check_availability()

    if available:
        print("🎉 ROOM AVAILABLE!")
        msg = (f"🏕️ Yosemite Valley Lodge 有房了！\n"
               f"📅 {CHECK_IN} → {CHECK_OUT}\n"
               f"⏰ {now}\n"
               f"👉 https://www.travelyosemite.com/lodging/yosemite-valley-lodge/?arrive=06/20/2026&depart=06/21/2026&adults=1&children=0")
        send_lark(msg)
        send_email("🏕️ Yosemite 有房了！", f"<h2>有房！</h2><p>{msg}</p>")
    else:
        print("No rooms available at this time.")

if __name__ == "__main__":
    main()
