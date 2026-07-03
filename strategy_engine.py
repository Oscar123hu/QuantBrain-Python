import pandas as pd
import numpy as np

def run_feature_engineering():
    print("🧠 启动 QuantBrain 矩阵大脑，加载本地真实历史行情...")
    
    # 1. 读取刚抓下来的真实比特币 CSV 账本
    try:
        df = pd.read_csv("crypto_market_data.csv")
    except FileNotFoundError:
        print("❌ 错误：找不到本地数据文件，请先运行 download_data.py！")
        return

    # 2. 彻底消除 for 循环，利用 Pandas 向量化滚动窗口（Rolling Window）压榨计算
    # 计算 20 周期均线（中轨）
    df["MA20"] = df["Close"].rolling(window=20).mean()
    
    # 计算 20 周期收盘价的标准差（离散度 \sigma）
    df["Std20"] = df["Close"].rolling(window=20).std()
    
    # 向量化矩阵直接相加减，一瞬间算出 1000 行数据的上下轨
    df["UpperBand"] = df["MA20"] + (2 * df["Std20"])
    df["LowerBand"] = df["MA20"] - (2 * df["Std20"])
    
    # 3. 机器学习特征衍生：计算当前价格偏离均线的百分比（作为一个极佳的动量统计特征）
    df["Price_Dist_MA"] = (df["Close"] - df["MA20"]) / df["MA20"]

    print("📈 向量化特征矩阵构建完毕，开始激发量化信号...")

    # 4. 向量化信号激发（完全不使用 if-else 循环判断）
    # 初始化信号列：0 代表空仓
    df["Signal"] = 0
    
    # 💡 策略逻辑：当收盘价跌破布林带下轨（超卖），向量化标记为 1（买入多头信号）
    df.loc[df["Close"] < df["LowerBand"], "Signal"] = 1
    
    # 💡 策略逻辑：当收盘价冲破布林带上轨（超买），向量化标记为 -1（卖出空头信号）
    df.loc[df["Close"] > df["UpperBand"], "Signal"] = -1

    # 5. 清洗掉因为窗口未满而产生的 NaN 空值
    df = df.dropna()

    # 6. 成果盘点：看看我们的策略在历史真实的比特币行情里抓到了多少次机会
    buy_signals = df[df["Signal"] == 1]
    sell_signals = df[df["Signal"] == -1]

    print("====================================================")
    print(f"📊 特征矩阵清洗完成！当前账本区间：{df['OpenTime'].iloc[0]} 至 {df['OpenTime'].iloc[-1]}")
    print(f"🔥 【多头狙击点触发】：{len(buy_signals)} 次（价格击穿下轨，抄底信号）")
    print(f"❄️ 【空头止盈点触发】：{len(sell_signals)} 次（价格冲破上轨，见顶信号）")
    print("====================================================")
    
    # 打印最后 5 行看看我们的完整特征矩阵大表
    preview_cols = ["OpenTime", "Close", "MA20", "UpperBand", "LowerBand", "Signal"]
    print("📋 最终量化特征矩阵数据快照（最后 5 行）：")
    print(df[preview_cols].tail(5))

if __name__ == "__main__":
    run_feature_engineering()