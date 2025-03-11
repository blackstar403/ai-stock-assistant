from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base

class Stock(Base):
    """股票基本信息模型"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    exchange = Column(String(20))
    currency = Column(String(10))
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    price_history = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    saved_stocks = relationship("SavedStock", back_populates="stock", cascade="all, delete-orphan")

class StockPrice(Base):
    """股票价格历史模型"""
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    # 关系
    stock = relationship("Stock", back_populates="price_history")
    
    class Config:
        # 复合唯一索引
        __table_args__ = (
            {"unique_together": ("stock_id", "date")},
        )

class SavedStock(Base):
    """用户保存的股票模型"""
    __tablename__ = "saved_stocks"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # 关系
    stock = relationship("Stock", back_populates="saved_stocks")

class AIAnalysisResult(Base):
    """AI分析结果模型"""
    __tablename__ = "ai_analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    summary = Column(Text)
    sentiment = Column(String(20))
    recommendation = Column(Text)
    risk_level = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    stock = relationship("Stock") 