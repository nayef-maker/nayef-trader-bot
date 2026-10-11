import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import os
from pybit.unified_trading import HTTP
import requests

# --- سيرفر الويب الوهمي لترضية منصة Render فقط ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

# تشغيل السيرفر في الخلفية
threading.Thread(target=run_dummy_server, daemon=True).start()
# -----------------------------------------------

def send_telegram_message(message):
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": message}
            requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def check_account_balance():
    try:
        api_key = os.getenv("BYBIT_API_KEY")
        api_secret = os.getenv("BYBIT_API_SECRET")
        if api_key and api_secret:
            session = HTTP(testnet=False, api_key=api_key, api_secret=api_secret)
            response = session.get_wallet_balance(accountType="UNIFIED")
            balance = response['result']['list'][0]['totalEquity']
            return float(balance)
    except Exception as e:
        print(f"⚠️ خطأ في قراءة رصيد بايبت: {e}")
    return 0.0

def main():
    print("🤖 بدأ تشغيل بوت بايبت ومسح السوق...")
    send_telegram_message("🤖 مرحباً أبو كياد! تم ربط البوت بنجاح وبدء مراقبة السوق.")
    
    while True:
        try:
            balance = check_account_balance()
            print(f"💰 الرصيد الحالي في المحفظة: {balance} USDT")
            
            # هنا يتم فحص السوق وتطبيق استراتيجية التبريد وبدون ستوب لوز
            print("⏳ جارٍ فحص السوق وانتظار الفرصة القادمة...")
            
        except Exception as e:
            print(f"❌ حدث خطأ أثناء دورة الفحص: {e}")
            
        # الانتظار لمدة 5 دقائق قبل الدورة التالية
        time.sleep(300)

if __name__ == "__main__":
    main()
