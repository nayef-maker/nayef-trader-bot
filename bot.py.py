import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
from pybit.unified_trading import HTTP
import requests

# --- سيرفر الويب الوهمي لترضية Render ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# ----------------------------------------

# --- مفاتيح بايبت الخاصة بك ---
BYBIT_API_KEY = "KH5jxrrRRAcbMV1os5"
BYBIT_API_SECRET = "h5HV5gibMoXkmZaSBcW8AZHgCkznGF2pFpiE"
# -------------------------------

def check_account_balance():
    try:
        session = HTTP(testnet=False, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)
        response = session.get_wallet_balance(accountType="UNIFIED")
        balance = response['result']['list'][0]['totalEquity']
        return float(balance)
    except Exception as e:
        print(f"⚠️ خطأ في قراءة رصيد بايبت: {e}")
    return 0.0

def main():
    print("🤖 بدأ تشغيل بوت بايبت ومسح السوق بنجاح...")
    
    while True:
        try:
            balance = check_account_balance()
            print(f"💰 الرصيد الحالي في المحفظة: {balance} USDT")
            print("⏳ جارٍ فحص السوق وانتظار الفرصة القادمة...")
        except Exception as e:
            print(f"❌ حدث خطأ أثناء دورة الفحص: {e}")
            
        time.sleep(300)

if __name__ == "__main__":
    main()
