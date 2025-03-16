import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.stock import Stock, StockPrice, SavedStock
from app.schemas.stock import StockInfo, StockPriceHistory, StockPricePoint
from app.services.data_sources.factory import DataSourceFactory

class StockService:
    """股票服务类，处理股票数据的获取和处理"""
    
    @staticmethod
    async def search_stocks(query: str, data_source: str = None) -> List[StockInfo]:
        """搜索股票"""
        data_source = DataSourceFactory.get_data_source(data_source)
        return await data_source.search_stocks(query)
    
    @staticmethod
    async def get_stock_info(symbol: str, data_source: str = None) -> Optional[StockInfo]:
        """获取股票详细信息"""
        data_source = DataSourceFactory.get_data_source(data_source)
        return await data_source.get_stock_info(symbol)
    
    @staticmethod
    async def get_stock_price_history(
        symbol: str, 
        interval: str = "daily", 
        range: str = "1m",
        data_source: str = None
    ) -> Optional[StockPriceHistory]:
        """获取股票历史价格数据"""
        data_source = DataSourceFactory.get_data_source(data_source)
        return await data_source.get_stock_price_history(symbol, interval, range)
    
    @staticmethod
    async def save_stock_to_db(db: Session, symbol: str, notes: Optional[str] = None) -> bool:
        """保存股票到数据库"""
        try:
            # 检查股票是否已存在
            stock = db.query(Stock).filter(Stock.symbol == symbol).first()
            
            # 如果股票不存在，获取信息并创建
            if not stock:
                stock_info = await StockService.get_stock_info(symbol)
                if not stock_info:
                    return False
                
                stock = Stock(
                    symbol=stock_info.symbol,
                    name=stock_info.name,
                    exchange=stock_info.exchange,
                    currency=stock_info.currency
                )
                db.add(stock)
                db.commit()
                db.refresh(stock)
            
            # 检查是否已保存
            saved_stock = db.query(SavedStock).filter(
                SavedStock.stock_id == stock.id
            ).first()
            
            # 如果未保存，创建保存记录
            if not saved_stock:
                saved_stock = SavedStock(
                    stock_id=stock.id,
                    notes=notes
                )
                db.add(saved_stock)
                db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            print(f"保存股票时出错: {str(e)}")
            return False
    
    @staticmethod
    async def get_saved_stocks(db: Session) -> List[Dict[str, Any]]:
        """获取已保存的股票列表"""
        try:
            saved_stocks = db.query(SavedStock).join(Stock).all()
            
            result = []
            for saved in saved_stocks:
                result.append({
                    "symbol": saved.stock.symbol,
                    "name": saved.stock.name,
                    "addedAt": saved.added_at.isoformat(),
                    "notes": saved.notes
                })
            
            return result
        except Exception as e:
            print(f"获取已保存股票时出错: {str(e)}")
            return []
    
    @staticmethod
    async def delete_saved_stock(db: Session, symbol: str) -> bool:
        """删除已保存的股票"""
        try:
            stock = db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock:
                return False
            
            saved_stock = db.query(SavedStock).filter(
                SavedStock.stock_id == stock.id
            ).first()
            
            if not saved_stock:
                return False
            
            db.delete(saved_stock)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"删除已保存股票时出错: {str(e)}")
            return False
            
    @staticmethod
    async def update_stock_data(symbol: str = None, db: Session = None) -> Dict[str, Any]:
        """更新股票数据
        
        如果指定了symbol，则只更新该股票的数据
        否则更新所有已保存的股票数据
        """
        try:
            if symbol:
                # 直接从数据源获取最新数据
                await StockService.get_stock_info(symbol)
                await StockService.get_stock_price_history(symbol)
                
                return {"success": True, "data": {"message": f"已更新股票 {symbol} 的数据"}}
            else:
                # 如果没有提供数据库会话，则只返回成功消息
                if db is None:
                    return {"success": True, "data": {"message": "已触发更新所有股票数据的任务"}}
                
                # 从数据库获取所有保存的股票
                try:
                    stocks = db.query(Stock).all()
                    updated_count = 0
                    
                    # 逐个更新股票数据
                    for stock in stocks:
                        try:
                            await StockService.get_stock_info(stock.symbol)
                            await StockService.get_stock_price_history(stock.symbol)
                            updated_count += 1
                        except Exception as e:
                            print(f"更新股票 {stock.symbol} 数据时出错: {str(e)}")
                    
                    return {
                        "success": True, 
                        "data": {
                            "message": f"已更新 {updated_count}/{len(stocks)} 个股票的数据"
                        }
                    }
                except Exception as e:
                    print(f"获取所有股票时出错: {str(e)}")
                    return {"success": False, "error": f"获取所有股票时出错: {str(e)}"}
        except Exception as e:
            print(f"更新股票数据时出错: {str(e)}")
            return {"success": False, "error": f"更新股票数据时出错: {str(e)}"}
    
    @staticmethod
    async def get_stock_intraday(
        symbol: str,
        refresh: bool = False,
        data_source: str = None
    ) -> Dict[str, Any]:
        """获取股票分时数据"""
        data_source = DataSourceFactory.get_data_source(data_source)
        return await data_source.get_intraday_data(symbol, refresh) 