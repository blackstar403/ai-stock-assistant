from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/analyze", response_model=dict)
async def analyze_stock(
    symbol: str = Query(..., description="股票代码"),
    data_source: Optional[str] = Query(None, description="数据源: alphavantage, tushare, akshare"),
    db: Session = Depends(get_db)
):
    """获取股票的 AI 分析"""
    analysis = await AIService.analyze_stock(symbol, data_source)
    
    if not analysis:
        return {
            "success": False,
            "error": "无法生成股票分析"
        }
    
    return {
        "success": True,
        "data": analysis
    } 