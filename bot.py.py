import time
import requests
import pandas as pd

# ==========================================
# 1. الإعدادات الأساسية (Telegram Bot)
# ==========================================
TELEGRAM_BOT_TOKEN = "8788563632:AAHLUL6Po-E5jLXFJQ_kdrDIFHz_3fJ2dvY"
TELEGRAM_CHAT_ID = "884123553"

TIMEFRAME = "30"

HALAL_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "NEARUSDT", "APTUSDT", "ATOMUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT", "XLMUSDT", "ALGOUSDT",
    "ICPUSDT", "FILUSDT", "VETUSDT", "QNTUSDT", "GRTUSDT", "AAVEUSDT", "EGLDUSDT", "SANDUSDT",
    "MANAUSDT", "AXSUSDT", "THETAUSDT", "FTMUSDT", "RUNEUSDT", "SNXUSDT", "KSMUSDT", "FLOWUSDT",
    "CHZUSDT", "ENJUSDT", "BATUSDT", "ZILUSDT", "COMPUSDT", "1INCHUSDT", "CRVUSDT", "LRCUSDT",
    "ANKRUSDT", "GALAUSDT", "ROSEUSDT", "KAVAUSDT", "IOTAUSDT", "NEOUSDT", "HOTUSDT", "QTUMUSDT",
    "OMGUSDT", "ZECUSDT", "DASHUSDT", "WAVESUSDT", "ICXUSDT", "ONTUSDT", "ZRXUSDT", "IOSTUSDT",
    "STORJUSDT", "SKLUSDT", "CELOUSDT", "OCEANUSDT", "BANDUSDT", "RENUSDT", "RLCUSDT", "KNCUSDT",
    "SXPUSDT", "OGNUSDT", "SPELLUSDT", "PEOPLEUSDT", "AGIXUSDT", "FETUSDT", "RNDRUSDT", "HIGHUSDT",
    "MINAUSDT", "ASTRUSDT"
]

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"خطأ تليجرام: {e}")

def get_klines(symbol, interval="30", limit=100):
    try:
        url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}&interval={interval}&limit={limit}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10).json()
        if res.get("retCode") == 0:
            list_data = res["result"]["list"]
            df = pd.DataFrame(list_data, columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"])
            df = df.iloc[::-1].reset_index(drop=True)
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)
            return df
    except Exception as e:
        print(f"خطأ جلب بيانات {symbol}: {e}")
    return None

def calculate_indicators(df):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    df['vol_ma'] = df['volume'].rolling(window=20).mean()
    df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
    return df

def check_golden_setup(df):
    if len(df) < 50:
        return False, {}
    
    sig_candle = df.iloc[-2]
    prev_candle = df.iloc[-3]
    confirm_candle = df.iloc[-1]
    
    score = 0
    factors = []
    
    if sig_candle['rsi'] <= 35:
        score += 1
        factors.append("تشبع بيعي (RSI <= 35)")
        
    body = abs(sig_candle['close'] - sig_candle['open'])
    lower_wick = min(sig_candle['open'], sig_candle['close']) - sig_candle['low']
    if lower_wick > (2 * body) and body > 0:
        score += 1
        factors.append("شمعة بين بار إيجابية")
        
    if sig_candle['volume'] > (1.5 * sig_candle['vol_ma']):
        score += 1
        factors.append("انفجار سيولة (Volume Spike)")
        
    if sig_candle['low'] < prev_candle['low'] and sig_candle['rsi'] > prev_candle['rsi']:
        score += 1
        factors.append("دايفرجنس إيجابي")
        
    if sig_candle['close'] >= sig_candle['ema200']:
        score += 1
        factors.append("فوق الاتجاه العام (EMA 200)")

    confirmation_passed = confirm_candle['close'] > sig_candle['close']
    
    if score >= 3 and confirmation_passed:
        stop_loss = sig_candle['low'] * 0.992
        details = {
            "score": score,
            "factors": factors,
            "entry_price": confirm_candle['close'],
            "stop_loss": stop_loss
        }
        return True, details
        
    return False, {}

def run_trading_bot():
    send_telegram_msg("🚀 تم إقلاع بوت نايف للتداول الآلي بنجاح (74 عملة + فريم 30د)")
    
    while True:
        try:
            for symbol in HALAL_SYMBOLS:
                df = get_klines(symbol, interval=TIMEFRAME)
                if df is not None:
                    df = calculate_indicators(df)
                    is_setup, details = check_golden_setup(df)
                    if is_setup:
                        send_telegram_msg(f"🎯 فرصة قوية مطابقة للشروط!\n- العملة: {symbol}\n- السعر: {details['entry_price']}\n- الشروط المتحققة: {len(details['factors'])}")
                time.sleep(1)
            time.sleep(300)
        except Exception as e:
            print(f"خطأ عام: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_trading_bot()
    import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check, daemon=True).start()
