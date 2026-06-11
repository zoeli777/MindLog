import smtplib
import os
import requests
from email.mime.text import MIMEText
from datetime import datetime
from playwright.sync_api import sync_playwright

CHECK_IN = "06/18/2026"
CHECK_OUT = "06/19/2026"
TARGET_EMAIL = "liqinrui1991@gmail.com"
LARK_WEBHOOK = os.environ.get("LARK_WEBHOOK")

def check_availability():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = f"https://www.travelyosemite.com/lodging/yosemite-valley-lodge/?arrive={CHECK_IN}&depart={CHECK_OUT}&adults=1&children=0"
        print(f"Loading: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(12000)

        # 找到 iframe
        frames = page.frames
        print(f"Total frames: {len(frames)}")
        for i, frame in enumerate(frames):
            print(f"Frame {i}: {frame.url}")

        # 在所有 frame 里搜索房间内容
        found = False
        for frame in frames:
            try:
                content = frame.content().lower()
                if "add to cart" in content or "per night" in content or "average/night" in content:
                    print(f"Found room content in frame: {frame.url}")
                    found = True
                    break
            except Exception as e:
                print(f"Frame error: {e}")

        browser.close()
        return found

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
    print(f"[{now}] Checking for {CHECK_IN} - {CHECK_OUT}")
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
        print("No rooms available.")

if __name__ == "__main__":
    main()
