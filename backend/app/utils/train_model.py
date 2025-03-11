"""
股票分析机器学习模型训练脚本

这个脚本用于训练一个简单的机器学习模型，用于预测股票的走势和风险水平。
模型将基于历史价格数据和技术指标进行训练。
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import sys
import random

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.config import settings

def generate_sample_data(n_samples=1000):
    """生成示例训练数据"""
    # 生成日期序列
    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_samples)
    dates = pd.date_range(start=start_date, end=end_date, periods=n_samples)
    
    # 生成特征
    data = {
        'date': dates,
        'close': np.random.normal(100, 10, n_samples).cumsum() + 1000,
        'volume': np.random.randint(1000000, 10000000, n_samples),
    }
    
    # 创建 DataFrame
    df = pd.DataFrame(data)
    
    # 添加技术指标
    # SMA
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 波动率
    df['volatility'] = df['close'].rolling(window=20).std()
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    
    # 添加目标变量
    # 1. 未来5天的价格变化百分比
    df['future_return'] = df['close'].shift(-5) / df['close'] - 1
    
    # 2. 走势标签 (1: 上涨, 0: 下跌)
    df['trend'] = (df['future_return'] > 0).astype(int)
    
    # 3. 风险水平 (0: 低, 1: 中, 2: 高)
    volatility_pct = df['volatility'] / df['close'] * 100
    df['risk'] = pd.cut(volatility_pct, bins=[0, 1, 3, float('inf')], labels=[0, 1, 2]).astype(int)
    
    # 4. 情绪标签 (0: 负面, 1: 中性, 2: 积极)
    df['sentiment'] = pd.cut(df['future_return'], bins=[-float('inf'), -0.02, 0.02, float('inf')], labels=[0, 1, 2]).astype(int)
    
    # 删除含有 NaN 的行
    df = df.dropna()
    
    return df

def train_models():
    """训练模型并保存"""
    # 生成示例数据
    df = generate_sample_data(1000)
    
    # 准备特征和目标变量
    features = ['sma_20', 'sma_50', 'rsi', 'volatility', 'macd', 'close', 'volume']
    X = df[features]
    y_trend = df['trend']
    y_risk = df['risk']
    y_sentiment = df['sentiment']
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 训练趋势预测模型
    trend_model = RandomForestClassifier(n_estimators=100, random_state=42)
    trend_model.fit(X_scaled, y_trend)
    
    # 训练风险预测模型
    risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
    risk_model.fit(X_scaled, y_risk)
    
    # 训练情绪预测模型
    sentiment_model = RandomForestClassifier(n_estimators=100, random_state=42)
    sentiment_model.fit(X_scaled, y_sentiment)
    
    # 创建模型目录
    os.makedirs(os.path.dirname(settings.AI_MODEL_PATH), exist_ok=True)
    
    # 保存模型
    model_data = {
        'scaler': scaler,
        'trend_model': trend_model,
        'risk_model': risk_model,
        'sentiment_model': sentiment_model,
        'features': features
    }
    
    joblib.dump(model_data, settings.AI_MODEL_PATH)
    print(f"模型已保存到 {settings.AI_MODEL_PATH}")

if __name__ == "__main__":
    train_models() 