import requests
import pandas as pd
from datetime import datetime

def fetch_crypto_data(symbol="BTCUSDT", interval="1h", limit=1000):
    print(f"🚀 开始从公开 API 轰炸抓取 {symbol} 的真实历史行情...")
    
    # 币安公开免签 K 线接口，不需要任何账号和 API Key
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit # 一次性抓取最近的 1000 根 K 线
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # 原始数据是一个大嵌套列表，我们需要把它规范化映射成表格
        columns = [
            "OpenTime", "Open", "High", "Low", "Close", "Volume",
            "CloseTime", "QuoteVolume", "TradesCount", "TakerBuyBase", "TakerBuyQuote", "Ignore"
        ]
        df = pd.DataFrame(data, columns=columns)
        
        # --- 核心大数据清洗与规整工程 ---
        # 1. 只保留量化回测最核心的 6 个维度（开高低收、成交量、交易笔数）
        keep_columns = ["OpenTime", "Open", "High", "Low", "Close", "Volume", "TradesCount"]
        df = df[keep_columns]
        
        # 2. 向量化时间戳转换：将原始的毫秒级时间戳（如 1672531199000）瞬间映射为可读的 YYYY-MM-DD HH:MM:SS
        df["OpenTime"] = pd.to_datetime(df["OpenTime"], unit='ms')
        
        # 3. 强制类型转换：API 返回的数字默认是字符串，必须全部变更为标准浮点数与高精度整数
        num_cols = ["Open", "High", "Low", "Close", "Volume"]
        df[num_cols] = df[num_cols].astype(float)
        df["TradesCount"] = df["TradesCount"].astype(int)
        
        # 4. 将清洗好的结构化数据保存到本地
        output_file = "crypto_market_data.csv"
        df.to_csv(output_file, index=False)
        
        print(f"✅ 成功！真实海量行情已完美落地至本地: {output_file}")
        print(f"📊 数据预览 (总计 {len(df)} 行)：")
        print(df.head(3)) # 打印前 3 行看看
        
    except Exception as e:
        print(f"❌ 抓取失败，错误原因: {e}")
        print("💡 提示：如果卡住，请确认你的科学上网工具是否开启了『TUN 模式』或『全局模式』。")

if __name__ == "__main__":
    fetch_crypto_data()