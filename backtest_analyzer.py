import pandas as pd
import numpy as np

def run_ultimate_backtest():
    print("🚀 启动 QuantBrain 终极资产评估引擎...")
    
    # 1. 自动运行并获取特征矩阵
    import strategy_engine
    df = pd.read_csv("crypto_market_data.csv")
    
    # 特征工程与信号矩阵构建（向量化）
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["Std20"] = df["Close"].rolling(window=20).std()
    df["UpperBand"] = df["MA20"] + (2 * df["Std20"])
    df["LowerBand"] = df["MA20"] - (2 * df["Std20"])
    
    df["Signal"] = 0
    df.loc[df["Close"] < df["LowerBand"], "Signal"] = 1
    df.loc[df["Close"] > df["UpperBand"], "Signal"] = -1
    df = df.dropna().copy()

    # 2. 核心量化资产回测流（向量化计算资产收益率，全程 0 循环）
    # 计算底层的市场波动率
    df["Market_Return"] = df["Close"].pct_change()
    
    # 策略持仓单周期收益率 = 昨天的信号 * 今天的市场波动率
    df["Strategy_Return"] = df["Signal"].shift(1) * df["Market_Return"]
    df = df.dropna()

    # 3. 统计学指标硬核计算
    total_market_return = (df["Market_Return"] + 1).prod() - 1
    total_strategy_return = (df["Strategy_Return"] + 1).prod() - 1
    
    # 计算年化波动率与夏普比率 (无风险利率设为 2%)
    annual_return = df["Strategy_Return"].mean() * 24 * 365
    annual_vol = df["Strategy_Return"].std() * np.sqrt(24 * 365)
    sharpe_ratio = (annual_return - 0.02) / annual_vol if annual_vol != 0 else 0
    
    # 计算最大回撤 (Max Drawdown)
    df["Cum_Return"] = (df["Strategy_Return"] + 1).cumprod()
    df["Cum_Max"] = df["Cum_Return"].cummax()
    df["Drawdown"] = (df["Cum_Return"] - df["Cum_Max"]) / df["Cum_Max"]
    max_drawdown = df["Drawdown"].min()

    print("\n====================================================")
    print("🎯 QUANTBRAIN QUANTITATIVE BACKTEST REPORT (终极报告)")
    print("====================================================")
    print(f"📊 测试资产范围  : BTC/USDT 永续行情流")
    print(f"📅 历史账本区间  : {df['OpenTime'].iloc[0]} 至 {df['OpenTime'].iloc[-1]}")
    print(f"📈 基准市场涨跌幅: {total_market_return * 100:.2f} %")
    print(f"💰 策略最终总收益: {total_strategy_return * 100:.2f} %")
    print(f"⚡ 策略年化波动率: {annual_vol * 100:.2f} %")
    print(f"🛡️ 核心最大回撤  : {max_drawdown * 100:.2f} %")
    print(f"🏆 统计学夏普比率: {sharpe_ratio:.4f}")
    print("====================================================")
    print("✅ 全链路大数据策略回测结束，指标完美落盘！")

if __name__ == "__main__":
    run_ultimate_backtest()