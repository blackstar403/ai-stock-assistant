from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.db.session import get_db, SessionLocal
from app.services.stock_service import StockService
from app.schemas.stock import StockInfo, StockPriceHistory
from app.core.config import settings
from app.utils.response import api_response

router = APIRouter()

# 创建一个包装函数，在任务执行时获取数据库会话
async def update_stock_data_with_db(symbol: str = None):
    """包装函数，在执行时创建数据库会话"""
    db = SessionLocal()
    try:
        return await StockService.update_stock_data(symbol, db)
    finally:
        db.close()

@router.get("/search", response_model=dict)
async def search_stocks(
    q: Optional[str] = Query(None, description="搜索关键词"),
    query: Optional[str] = Query(None, description="搜索关键词（与q参数二选一）"),
    data_source: Optional[str] = Query(None, description="数据源: alphavantage, tushare, akshare"),
    db: Session = Depends(get_db)
):
    """搜索股票"""
    # 使用q或query参数，优先使用q
    search_term = q or query
    
    if not search_term:
        return api_response(success=False, error="请提供搜索关键词（使用q或query参数）")
    
    results = await StockService.search_stocks(search_term, data_source)
    return api_response(data=results)

@router.get("/{symbol}", response_model=dict)
async def get_stock_info(
    symbol: str,
    data_source: Optional[str] = Query(None, description="数据源: alphavantage, tushare, akshare"),
    db: Session = Depends(get_db)
):
    """获取股票详细信息"""
    stock_info = await StockService.get_stock_info(symbol, data_source)
    if not stock_info:
        return api_response(success=False, error="未找到股票信息")

    return api_response(data=stock_info)

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
        return api_response(success=False, error=f"无效的间隔参数。有效值: {', '.join(valid_intervals)}")
    
    if range not in valid_ranges:
        return api_response(success=False, error=f"无效的时间范围参数。有效值: {', '.join(valid_ranges)}")
    
    price_history = await StockService.get_stock_price_history(symbol, interval, range, data_source)
    if not price_history:
        return api_response(success=False, error="获取股票历史价格失败")
    
    return api_response(data=price_history)

# 添加AI分析接口，与前端路径匹配
@router.get("/{symbol}/analysis", response_model=dict)
async def get_stock_analysis(
    symbol: str,
    data_source: Optional[str] = Query(None, description="数据源: alphavantage, tushare, akshare"),
    db: Session = Depends(get_db)
):
    """获取股票的AI分析"""
    from app.services.ai_service import AIService
    
    analysis = await AIService.analyze_stock(symbol, data_source)
    if not analysis:
        return api_response(success=False, error="无法生成股票分析")
    
    return api_response(data=analysis)

@router.post("/{symbol}/update")
async def update_stock_data(symbol: str, background_tasks: BackgroundTasks):
    """手动更新特定股票数据"""
    background_tasks.add_task(update_stock_data_with_db, symbol)
    return api_response(data={"message": f"开始更新股票 {symbol} 的数据"})

@router.post("/update-all")
async def update_all_stocks(background_tasks: BackgroundTasks):
    """手动更新所有股票数据"""
    background_tasks.add_task(update_stock_data_with_db)
    return api_response(data={"message": "开始更新所有股票数据"})