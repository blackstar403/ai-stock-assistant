from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.services.stock_service import StockService
from app.schemas.stock import StockInfo, StockPriceHistory
from app.core.config import settings

router = APIRouter()

@router.get("/search", response_model=dict)
async def search_stocks(
    q: str = Query(..., description="搜索关键词"),
    data_source: Optional[str] = Query(None, description="数据源: alphavantage, tushare, akshare"),
    db: Session = Depends(get_db)
):
    """搜索股票"""
    results = await StockService.search_stocks(q, data_source)
    return {
        "success": True,
        "data": results
    }

@router.get("/{symbol}", response_model=dict)
async def get_stock_info(
    symbol: str,
    data_source: Optional[str] = Query(None, description="数据源: alphavantage, tushare, akshare"),
    db: Session = Depends(get_db)
):
    """获取股票详细信息"""
    stock_info = await StockService.get_stock_info(symbol, data_source)
    if not stock_info:
        return {
            "success": False,
            "error": "未找到股票信息"
        }
    
    return {
        "success": True,
        "data": stock_info
    }

@router.get("/{symbol}/history", response_model=dict)
async def get_stock_price_history(
    symbol: str,
    interval: str = Query("daily", description="数据间隔: daily, weekly, monthly"),
    range: str = Query("1m", description="时间范围: 1m, 3m, 6m, 1y, 5y"),
    data_source: Optional[str] = Query(None, description="数据源: alphavantage, tushare, akshare"),
    db: Session = Depends(get_db)
):
    """获取股票历史价格数据"""
    # 验证参数
    valid_intervals = ["daily", "weekly", "monthly"]
    valid_ranges = ["1m", "3m", "6m", "1y", "5y"]
    
    if interval not in valid_intervals:
        return {
            "success": False,
            "error": f"无效的间隔参数。有效值: {', '.join(valid_intervals)}"
        }
    
    if range not in valid_ranges:
        return {
            "success": False,
            "error": f"无效的时间范围参数。有效值: {', '.join(valid_ranges)}"
        }
    
    price_history = await StockService.get_stock_price_history(symbol, interval, range, data_source)
    if not price_history:
        return {
            "success": False,
            "error": "获取股票历史价格失败"
        }
    
    return {
        "success": True,
        "data": price_history
    } 