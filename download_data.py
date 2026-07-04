import requests
import pandas as pd

def fetch_crypto_data(symbol="BTCUSDT", interval="1h", limit=1000):
    """
    Fetch historical klines from Binance Public API and sanitize schema.
    """
    print(f"[INFO] Fetching market data for {symbol} ({interval})...")
    
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Check API restrictions/errors
        if isinstance(data, dict):
            print(f"[ERROR] API rejection. Details: {data}")
            return
        
        # Raw columns mapping
        columns = [
            "OpenTime", "Open", "High", "Low", "Close", "Volume",
            "CloseTime", "QuoteVolume", "TradesCount", "TakerBuyBase", "TakerBuyQuote", "Ignore"
        ]
        df = pd.DataFrame(data, columns=columns)
        
        # Target feature extraction
        keep_cols = ["OpenTime", "Open", "High", "Low", "Close", "Volume", "TradesCount"]
        df = df[keep_cols]
        
        # Vectorized timestamp parsing and type casting
        df["OpenTime"] = pd.to_datetime(df["OpenTime"], unit='ms')
        numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
        df[numeric_cols] = df[numeric_cols].astype(float)
        df["TradesCount"] = df["TradesCount"].astype(int)
        
        df.to_csv("crypto_market_data.csv", index=False)
        print(f"[SUCCESS] Dataset synchronized. Shape: {df.shape}")
        
    except Exception as e:
        print(f"[CRITICAL] Network or parsing exception encountered: {e}")

if __name__ == "__main__":
    fetch_crypto_data()