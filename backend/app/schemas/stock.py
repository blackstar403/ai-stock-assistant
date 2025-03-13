from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 股票基本信息模型
class StockBase(BaseModel):
    symbol: str
    name: str
    exchange: str
    currency: str

class StockCreate(StockBase):
    pass

class StockInfo(StockBase):
    price: Optional[float] = None
    change: Optional[float] = None
    changePercent: Optional[float] = None
    marketCap: Optional[float] = None
    volume: Optional[int] = None
    
    class Config:
        from_attributes = True

# 股票价格历史数据点
class StockPricePoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

# 股票历史价格数据
class StockPriceHistory(BaseModel):
    symbol: str
    data: List[StockPricePoint]

# AI分析结果
class AIAnalysis(BaseModel):
    summary: str
    sentiment: str = Field(..., description="positive, neutral, negative")
    keyPoints: List[str]
    recommendation: str
    riskLevel: str = Field(..., description="low, medium, high")
    analysisType: Optional[str] = Field(None, description="rule, ml, llm")

# 用户保存的股票
class SavedStockCreate(BaseModel):
    symbol: str
    notes: Optional[str] = None

class SavedStock(BaseModel):
    symbol: str
    name: str
    addedAt: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()  # 将datetime序列化为ISO格式字符串
        }

# API响应
class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None 