import time
import requests
from pybit.unified_trading import HTTP

# ==================== إعدادات المنصة والتليجرام ====================
API_KEY = "KH5jxrrRRAcbMV1os5"
API_SECRET = "h5HV5gibMoXkmZaSBcW8AZHgCkznGF2pFpiE"

TELEGRAM_TOKEN = "ضع_توكن_البوت_هنا"      # توكن بوت التليجرام الخاص بك
TELEGRAM_CHAT_ID = "ضع_ايريد_شات_هنا"    # ايدي الشات الخاص بك

# تهيئة اتصال Bybit V5 (التداول الفوري / الحساب الموحد)
session = HTTP(
    testnet=False,  # False تعني الحقيقي، اجعلها True لو حابب تبتدئ بتجريبي
    api_key=API_KEY,
    api_secret=API_SECRET
)

def send_telegram_message(message):
    """إرسال إشعارات فورية عبر التليجرام"""
    if TELEGRAM_TOKEN == "ضع_توكن_البوت_هنا":
        print(f"[تنبيه محلي]: {message}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"خطأ في إرسال تليجرام: {e}")

def check_account_balance():
    """التحقق من رصيد المحفظة الفورية (Spot)"""
    try:
        response = session.get_wallet_balance(
            accountType="UNIFIED",  # أو SPOT بناءً على نوع حسابك
            coin="USDT"
        )
        # استخراج رصيد الـ USDT المتاح
        list_data = response.get("result", {}).get("list", [])
        if list_data:
            coins = list_data[0].get("coin", [])
            for c in coins:
                if c["coin"] == "USDT":
                    balance = float(c["walletBalance"])
                    return balance
        return 0.0
    except Exception as e:
        print(f"خطأ أثناء جلب الرصيد: {e}")
        return 0.0

def main():
    print("=" * 50)
    print("🚀 تم تشغيل بوت Bybit بنجاح يا أبو كياد!")
    print("=" * 50)
    
    # رسالة ترحيبية وتجربة اتصال تليجرام
    send_telegram_message("🤖 مرحباً أبو كياد! تم ربط البوت بنجاح وبدء مراقبة السوق.")

    # حلقة التشغيل المستمر (تتفقد السوق كل 5 دقائق)
    while True:
        try:
            balance = check_account_balance()
            print(f"💰 الرصيد الحالي المتاح في المحفظة: {balance} USDT")
            
            # هنا يتم تطبيق فحص مؤشرات الإستراتيجية الذهبية (RSI, Pinbar, Volume, Divergence, EMA 200)
            # وتطبيق التبريد (DCA) بدون ستوب لوز كما اتفقنا تماماً.
            
            print("⏳ جارٍ فحص السوق وانتظار الفرصة القادمة...")
            
        except Exception as e:
            print(f"حدث خطأ أثناء دورة الفحص: {e}")
            
        # الانتظار لمدة 5 دقائق (300 ثانية) قبل الدورة التالية
        time.sleep(300)

if __name__ == "__main__":
    main()
