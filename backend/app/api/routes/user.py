from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.services.stock_service import StockService
from app.schemas.stock import SavedStockCreate

router = APIRouter()

@router.get("/saved-stocks", response_model=dict)
async def get_saved_stocks(
    db: Session = Depends(get_db)
):
    """获取用户保存的股票列表"""
    saved_stocks = await StockService.get_saved_stocks(db)
    
    return {
        "success": True,
        "data": saved_stocks
    }

@router.post("/saved-stocks", response_model=dict)
async def save_stock(
    stock_data: SavedStockCreate,
    db: Session = Depends(get_db)
):
    """保存股票到收藏夹"""
    success = await StockService.save_stock_to_db(
        db, 
        stock_data.symbol, 
        stock_data.notes
    )
    
    if not success:
        return {
            "success": False,
            "error": "保存股票失败"
        }
    
    return {
        "success": True
    }

@router.delete("/saved-stocks/{symbol}", response_model=dict)
async def delete_saved_stock(
    symbol: str,
    db: Session = Depends(get_db)
):
    """从收藏夹中删除股票"""
    success = await StockService.delete_saved_stock(db, symbol)
    
    if not success:
        return {
            "success": False,
            "error": "删除股票失败"
        }
    
    return {
        "success": True
    } 