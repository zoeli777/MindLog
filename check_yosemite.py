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
    search_url = "https://reservations.ahlsmsworld.com/Yosemite/Plan-Your-Trip/Accommodation-Search"
    r1 = session.get(search_url, timeout=20)
    print(f"Step 1 status: {r1.status_code}")
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
    results_url = "https://reservations.ahlsmsworld.com/Yosemite/Plan-Your-Trip/Accommodation-Search/Results"
    r3 = session.get(results_url, timeout=20)
    print(f"Step 3 status: {r3.status_code}, length: {len(r3.text)}")
    content = r3.text.lower()
    print("=== SNIPPET (10000-13000) ===")
    print(r3.text[10000:13000])
    print("=== END ===")
    has_room = "add to cart" in content or "addtocart" in content or "per night" in content
    print(f"Has room: {has_room}")
    return has_room

def send_lark(message):
    if not LARK_WEBHOOK:
        return
    try:
        resp = requests.post(LARK_WEBHOOK, json={
            "msg_type": "text",
            "content": {"text": message}
        }, timeout=10)
        print(f"Lark sent: {resp.status_code}")
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
        print("ROOM AVAILABLE!")
        msg = (f"Yosemite Valley Lodge 有房了！\n"
               f"入住：{CHECK_IN} 退房：{CHECK_OUT}\n"
               f"时间：{now}\n"
               f"预订：https://www.travelyosemite.com/lodging/yosemite-valley-lodge/?arrive=06/20/2026&depart=06/21/2026&adults=1&children=0")
        send_lark(msg)
        send_email("Yosemite 有房了！", f"<h2>有房！</h2><p>{msg}</p>")
    else:
        print("No rooms available at this time.")

if __name__ == "__main__":
    main()
