import os
import time
import requests
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==========================================
# 1. إعدادات السيرفر (Health Check)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    print(f"[SERVER] بدء تشغيل سيرفر الـ Health Check على المنفذ {port}")
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ==========================================
# 2. إعدادات التليجرام والعملات
# ==========================================
TELEGRAM_BOT_TOKEN = "8788563632:AAHLUL6Po-E5jLXF3Q_kdrDIFHz_3fJ2dVY"
TELEGRAM_CHAT_ID = "884123553"
TIMEFRAME = "30"

HALAL_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "NEARUSDT", "APTUSDT", "ATOMUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT", "XLMUSDT", "ALGOUSDT",
    "ICPUSDT", "FILUSDT", "VETUSDT", "QNTUSDT", "AAVEUSDT", "EGLDUSDT", "SANDUSDT", "MANAUSDT",
    "AXSUSDT", "THETAUSDT", "FTMUSDT", "RUNEUSDT", "SNXUSDT", "KSMUSDT", "FLOWUSDT"
]

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        res = requests.post(url, json=payload, timeout=10)
        print(f"[TELEGRAM] نتيجة الإرسال: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[TELEGRAM ERROR] خطأ في إرسال تليجرام: {e}")

def get_klines(symbol, interval="30", limit=100):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}m&limit={limit}"
        res = requests.get(url, timeout=10)
        data = res.json()
        df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', '', '', '', '', '', ''])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print(f"[BINANCE ERROR] خطأ في جلب بيانات {symbol}: {e}")
        return None

def calculate_indicators(df):
    df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
    return df

def check_golden_setup(df):
    if len(df) < 2:
        return False, {}
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    
    if prev['EMA_50'] <= prev['EMA_200'] and curr['EMA_50'] > curr['EMA_200']:
        return True, {'entry_price': curr['close']}
    return False, {}

def run_trading_bot():
    print("[BOT] بدأت دالة run_trading_bot بنجاح، جاري إرسال رسالة الإقلاع...")
    send_telegram_msg("🚀 تم إقلاع بوت نايف للسيجنال بنجاح وتفعيل المراقبة الآلية!")
    
    while True:
        try:
            print("[BOT] بدء دورة فحص العملات الجديدة...")
            for symbol in HALAL_SYMBOLS:
                df = get_klines(symbol, interval=TIMEFRAME)
                if df is not None:
                    df = calculate_indicators(df)
                    is_setup, details = check_golden_setup(df)
                    if is_setup:
                        send_telegram_msg(f"🎯 فرصة قوية مطابقة للشروط!\n- العملة: {symbol}\n- السعر: {details['entry_price']}")
                time.sleep(1)
            print("[BOT] انتهى فحص جميع العملات، جاري الانتظار 5 دقائق...")
            time.sleep(300)
        except Exception as e:
            print(f"[BOT ERROR] خطأ عام في حلقة التداول: {e}")
            time.sleep(30)

if __name__ == "__main__":
    # تشغيل السيرفر في الخلفية لإرضاء Render
    server_thread = threading.Thread(target=run_health_check, daemon=True)
    server_thread.start()
    
    # تشغيل البوت في الخيط الرئيسي مباشرة لضمان عدم توقفه
    run_trading_bot()
