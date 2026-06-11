import requests
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime

# 监控配置
CHECK_IN = "06/20/2026"
CHECK_OUT = "06/21/2026"
TARGET_EMAIL = "liqinrui1991@gmail.com"

def check_page_availability():
    """抓取搜索结果页面，精准判断是否有房"""
    url = "https://www.travelyosemite.com/lodging/yosemite-valley-lodge/"
    params = {
        "arrive": CHECK_IN,
        "depart": CHECK_OUT,
        "adults": "1",
        "children": "0",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        content = resp.text
        content_lower = content.lower()
        print(f"Page status: {resp.status_code}, length: {len(content)}")

        # 明确无房的标志（优先判断）
        no_room_phrases = [
            "no rooms available",
            "no availability",
            "sold out",
            "there are no rooms",
            "no lodging available",
            "0 results",
            "showing 0",
        ]
        for phrase in no_room_phrases:
            if phrase in content_lower:
                print(f"No room phrase found: '{phrase}'")
                return False, content

        # 必须同时出现这些关键词才算真正有房
        has_add_to_cart = "add to cart" in content_lower
        has_price = "average/night" in content_lower or "per night" in content_lower
        has_showing = "showing 1 to" in content_lower

        print(f"add to cart: {has_add_to_cart}, price: {has_price}, showing results: {has_showing}")

        if has_add_to_cart and has_price and has_showing:
            return True, content
        else:
            return False, content

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
    print(f"[{now}] Checking Yosemite Valley Lodge for {CHECK_IN} - {CHECK_OUT}")

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
