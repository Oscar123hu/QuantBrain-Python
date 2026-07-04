import requests
import pandas as pd
import numpy as np

def fetch_crypto_data(symbol="BTCUSDT", interval="1h", limit=1000):
    """
    流式抓取交易所历史行情并执行数据清洗
    """
    print(f"[INFO] 正在同步 {symbol} ({interval}) 历史市场行情数据...")
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if isinstance(data, dict):
            print(f"[ERROR] 交易所接口拒绝访问。详细信息: {data}")
            return False
        
        columns = [
            "OpenTime", "Open", "High", "Low", "Close", "Volume",
            "CloseTime", "QuoteVolume", "TradesCount", "TakerBuyBase", "TakerBuyQuote", "Ignore"
        ]
        df = pd.DataFrame(data, columns=columns)
        
        keep_cols = ["OpenTime", "Open", "High", "Low", "Close", "Volume", "TradesCount"]
        df = df[keep_cols]
        df["OpenTime"] = pd.to_datetime(df["OpenTime"], unit='ms')
        
        numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
        df[numeric_cols] = df[numeric_cols].astype(float)
        df["TradesCount"] = df["TradesCount"].astype(int)
        
        df.to_csv("crypto_market_data.csv", index=False)
        print(f"[SUCCESS] 历史数据同步完成。数据矩阵维度: {df.shape}")
        return True
    except Exception as e:
        print(f"[CRITICAL] 数据获取层发生异常: {e}")
        return False

def compute_bollinger_signals(df, window=20, n_std=2):
    """
    基于向量化矩阵计算布林带指标并激发交易信号
    """
    df["MA20"] = df["Close"].rolling(window=window).mean()
    df["Std20"] = df["Close"].rolling(window=window).std()
    
    df["UpperBand"] = df["MA20"] + (n_std * df["Std20"])
    df["LowerBand"] = df["MA20"] - (n_std * df["Std20"])
    
    df["Signal"] = 0
    df.loc[df["Close"] < df["LowerBand"], "Signal"] = 1
    df.loc[df["Close"] > df["UpperBand"], "Signal"] = -1
    return df.dropna().copy()

def run_backtest_pipeline():
    """
    执行向量化回测流水线并解析核心风控指标
    """
    print("[INFO] 正在初始化量化回测...")
    try:
        raw_df = pd.read_csv("crypto_market_data.csv")
    except FileNotFoundError:
        print("[ERROR] 未找到本地历史数据账本。")
        return

    df = compute_bollinger_signals(raw_df)
    
    # 向量化收益率计算（通过 shift 引入滞后一期，规避未来函数陷阱）
    df["Market_Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Signal"].shift(1) * df["Market_Return"]
    df = df.dropna()

    total_market = (df["Market_Return"] + 1).prod() - 1
    total_strategy = (df["Strategy_Return"] + 1).prod() - 1
    
    ann_factor = 24 * 365
    annual_return = df["Strategy_Return"].mean() * ann_factor
    annual_vol = df["Strategy_Return"].std() * np.sqrt(ann_factor)
    sharpe = (annual_return - 0.02) / annual_vol if annual_vol != 0 else 0
    
    df["Cum_Return"] = (df["Strategy_Return"] + 1).cumprod()
    df["Cum_Max"] = df["Cum_Return"].cummax()
    max_dd = ((df["Cum_Return"] - df["Cum_Max"]) / df["Cum_Max"]).min()

    print("\n----------------------------------------------------")
    print("           QuantBrain 量化回测执行报告           ")
    print("----------------------------------------------------")
    print(f" 测试标的      : BTC/USDT 现货/永续行情流")
    print(f" 回测周期      : {df['OpenTime'].iloc[0]} -> {df['OpenTime'].iloc[-1]}")
    print(f" 基准收益率    : {total_market * 100:.2f}%")
    print(f" 策略总收益    : {total_strategy * 100:.2f}%")
    print(f" 年化波动率    : {annual_vol * 100:.2f}%")
    print(f" 最大回撤      : {max_dd * 100:.2f}%")
    print(f" 夏普比率      : {sharpe:.4f}")
    print("----------------------------------------------------")

if __name__ == "__main__":
    if fetch_crypto_data():
        run_backtest_pipeline()