import time
import requests

# Binance public API se BTC ki price check karne ka simple bot
def get_binance_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        price = float(data['price'])
        return price
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def main():
    print("Binance Alert Bot started successfully!")
    while True:
        current_price = get_binance_price()
        if current_price:
            print(f"Current BTC Price: ${current_price}")
            
            # Yahan aap apni pasand ka koi bhi price alert condition laga sakte hain
            if current_price > 90000:
                print("ALERT: BTC price crossed $90,000!")
                
        # Har 60 seconds baad price check karega
        time.sleep(60)

if __name__ == "__main__":
    main()
