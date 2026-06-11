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
        page = browser.new_page()
        
        url = (f"https://www.travelyosemite.com/lodging/yosemite-valley-lodge/"
               f"?arrive={CHECK_IN}&depart={CHECK_OUT}&adults=1&children=0")
        
        print(f"Loading: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(15000)

        # 调试：打印页面中间部分
        content = page.content()
        print("=== SNIPPET (220000-225000) ===")
        print(content[220000:225000])
        print("=== END ===")        
        
        content = page.content().lower()
        print(f"Page loaded, length: {len(content)}")
        
        # 截图调试（可选）
        # page.screenshot(path="screenshot.png")
        
        has_add_to_cart = "add to cart" in content
        has_price = "average/night" in content or "per night" in content
        has_showing = "showing 1 to" in content
        
        print(f"add to cart: {has_add_to_cart}, price: {has_price}, showing: {has_showing}")
        
        browser.close()
        return has_add_to_cart and has_price and has_showing

def send_lark(message):
    if not LARK_WEBHOOK:
        print("Lark webhook not set")
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
        print("🎉 ROOM AVAILABLE!")
        msg = (f"🏕️ Yosemite Valley Lodge 有房了！\n"
               f"📅 {CHECK_IN} → {CHECK_OUT}\n"
               f"⏰ {now}\n"
               f"👉 https://www.travelyosemite.com/lodging/yosemite-valley-lodge/?arrive=06/20/2026&depart=06/21/2026&adults=1&children=0")
        send_lark(msg)
        send_email("🏕️ Yosemite 有房了！", f"<h2>有房！</h2><p>{msg.replace(chr(10), '<br>')}</p>")
    else:
        print("No rooms available at this time.")

if __name__ == "__main__":
    main()
