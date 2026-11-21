import time
import requests
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIGURATION SETTINGS =================
VOLATILITY_TIMEFRAME_MINUTES = 5  # Volatility check karne ka time (e.g., 5 minutes)
VOLATILITY_THRESHOLD_PCT = 5.0    # Price change percentage limit (e.g., 5%)
RSI_PERIOD = 14                   # RSI period
RSI_OVERBOUGHT = 80               # Overbought level
RSI_OVERSOLD = 20                 # Oversold level
CHECK_INTERVAL_SECONDS = 60       # Bot har kitne seconds baad market scan karega
# ==========================================================

def get_binance_futures_symbols():
    """Binance Futures ke tamam active trading pairs fetch karta hai."""
    try:
        url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        response = requests.get(url, timeout=10)
        data = response.json()
        symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT']
        return symbols
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return []

def get_historical_klines(symbol, interval='5m', limit=30):
    """Historical candles data lane ke liye."""
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if isinstance(data, list):
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                             'close_time', 'quote_asset_volume', 'trades', 
                                             'taker_buy_base', 'taker_buy_quote', 'ignore'])
            df['close'] = df['close'].astype(float)
            df['open'] = df['open'].astype(float)
            return df
    except Exception as e:
        pass
    return None

def calculate_rsi(series, period=14):
    """RSI calculate karne ka function."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_symbol(symbol, interval_str):
    """Aik single symbol ko analyze karne ka function (Multi-threading ke liye)."""
    df = get_historical_klines(symbol, interval=interval_str, limit=30)
    if df is not None and len(df) >= RSI_PERIOD + 2:
        # 1. Volatility Check
        open_price = df['open'].iloc[-1]
        close_price = df['close'].iloc[-1]
        price_change = ((close_price - open_price) / open_price) * 100

        if abs(price_change) >= VOLATILITY_THRESHOLD_PCT:
            direction = "PUMP 🚀" if price_change > 0 else "DUMP 🩸"
            print(f"[VOLATILITY ALERT] {symbol}: {direction} | Change: {price_change:.2f}% in last {VOLATILITY_TIMEFRAME_MINUTES}m")

        # 2. RSI Check
        df['rsi'] = calculate_rsi(df['close'], period=RSI_PERIOD)
        current_rsi = df['rsi'].iloc[-1]

        if current_rsi >= RSI_OVERBOUGHT:
            print(f"[RSI OVERBOUGHT ALERT] {symbol}: RSI is at {current_rsi:.2f} (>= {RSI_OVERBOUGHT})")
        elif current_rsi <= RSI_OVERSOLD:
            print(f"[RSI OVERSOLD ALERT] {symbol}: RSI is at {current_rsi:.2f} (<= {RSI_OVERSOLD})")

def scan_market():
    print(f"\n--- Binance Futures Super-Fast Scan Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    symbols = get_binance_futures_symbols()
    print(f"Total active Futures tokens found: {len(symbols)}")

    interval_str = f"{VOLATILITY_TIMEFRAME_MINUTES}m" if VOLATILITY_TIMEFRAME_MINUTES < 60 else "1h"

    # Multi-threading use kar rahe hain taake saare coins aik sath (parallel) check hon
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(analyze_symbol, symbol, interval_str) for symbol in symbols]
        for future in as_completed(futures):
            pass  # Sab threads ke complete hone ka intezar

    print(f"--- Scan Completed. Waiting for next cycle ---\n")

def main():
    print("Binance Futures Advanced Alert Bot Started Successfully!")
    while True:
        try:
            scan_market()
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
