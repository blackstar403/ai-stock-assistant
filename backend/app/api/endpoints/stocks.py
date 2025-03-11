from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.schemas.stock import StockInfo, StockHistory, StockSearch, AIAnalysis
from app.services.stock_service import StockService
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/search", response_model=List[StockSearch])
async def search_stocks(
    q: str = Query(..., description="搜索关键词"),
    data_source: Optional[str] = Query(None, description="数据源，可选值: alphavantage, tushare, akshare")
):
    """搜索股票"""
    results = await StockService.search_stocks(q, data_source)
    if not results:
        return []
    return results

@router.get("/{symbol}", response_model=StockInfo)
async def get_stock_info(
    symbol: str,
    data_source: Optional[str] = Query(None, description="数据源，可选值: alphavantage, tushare, akshare")
):
    """获取股票信息"""
    stock_info = await StockService.get_stock_info(symbol, data_source)
    if not stock_info:
        raise HTTPException(status_code=404, detail=f"未找到股票: {symbol}")
    return stock_info

@router.get("/{symbol}/history", response_model=List[StockHistory])
async def get_stock_history(
    symbol: str,
    interval: str = Query("daily", description="时间间隔，可选值: daily, weekly, monthly"),
    data_source: Optional[str] = Query(None, description="数据源，可选值: alphavantage, tushare, akshare")
):
    """获取股票历史数据"""
    history = await StockService.get_stock_history(symbol, interval, data_source)
    if not history:
        raise HTTPException(status_code=404, detail=f"未找到股票历史数据: {symbol}")
    return history

@router.get("/{symbol}/analysis", response_model=AIAnalysis)
async def get_stock_analysis(
    symbol: str,
    data_source: Optional[str] = Query(None, description="数据源，可选值: alphavantage, tushare, akshare"),
    analysis_mode: Optional[str] = Query(None, description="分析模式，可选值: rule, ml, llm")
):
    """获取股票AI分析"""
    analysis = await AIService.analyze_stock(symbol, data_source, analysis_mode)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"无法生成股票分析: {symbol}")
    return analysis 