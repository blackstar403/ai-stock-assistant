import requests
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime

from app.core.config import settings
from app.services.data_sources.base import DataSourceBase
from app.schemas.stock import StockInfo, StockPriceHistory, StockPricePoint

class AlphaVantageDataSource(DataSourceBase):
    """Alpha Vantage 数据源实现"""
    
    def __init__(self):
        self.base_url = settings.ALPHAVANTAGE_API_BASE_URL
        self.api_key = settings.ALPHAVANTAGE_API_KEY
    
    async def search_stocks(self, query: str) -> List[StockInfo]:
        """搜索股票"""
        try:
            # 调用 Alpha Vantage API 搜索股票
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": query,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "bestMatches" not in data:
                return []
            
            results = []
            for match in data["bestMatches"]:
                stock_info = StockInfo(
                    symbol=match.get("1. symbol", ""),
                    name=match.get("2. name", ""),
                    exchange=match.get("4. region", ""),
                    currency=match.get("8. currency", "USD")
                )
                results.append(stock_info)
            
            return results
        except Exception as e:
            print(f"搜索股票时出错: {str(e)}")
            return []
    
    async def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """获取股票详细信息"""
        try:
            # 调用 Alpha Vantage API 获取股票详情
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            quote_data = response.json()
            
            # 获取公司概览
            params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": self.api_key
            }
            overview_response = requests.get(self.base_url, params=params)
            overview_data = overview_response.json()
            
            if "Global Quote" not in quote_data or not overview_data:
                return None
            
            quote = quote_data["Global Quote"]
            
            # 构建股票信息
            stock_info = StockInfo(
                symbol=symbol,
                name=overview_data.get("Name", ""),
                exchange=overview_data.get("Exchange", ""),
                currency=overview_data.get("Currency", "USD"),
                price=float(quote.get("05. price", 0)),
                change=float(quote.get("09. change", 0)),
                changePercent=float(quote.get("10. change percent", "0%").replace("%", "")),
                marketCap=float(overview_data.get("MarketCapitalization", 0)),
                volume=int(quote.get("06. volume", 0))
            )
            
            return stock_info
        except Exception as e:
            print(f"获取股票信息时出错: {str(e)}")
            return None
    
    async def get_stock_price_history(
        self, 
        symbol: str, 
        interval: str = "daily", 
        range: str = "1m"
    ) -> Optional[StockPriceHistory]:
        """获取股票历史价格数据"""
        try:
            # 映射时间范围到 Alpha Vantage 的输出大小
            output_size = "compact" if range in ["1m", "3m"] else "full"
            
            # 映射间隔到 Alpha Vantage 的函数
            function_map = {
                "daily": "TIME_SERIES_DAILY",
                "weekly": "TIME_SERIES_WEEKLY",
                "monthly": "TIME_SERIES_MONTHLY"
            }
            
            function = function_map.get(interval, "TIME_SERIES_DAILY")
            
            # 调用 Alpha Vantage API
            params = {
                "function": function,
                "symbol": symbol,
                "outputsize": output_size,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            # 提取时间序列数据
            time_series_key = next((k for k in data.keys() if "Time Series" in k), None)
            if not time_series_key:
                return None
            
            time_series = data[time_series_key]
            
            # 转换为 DataFrame 进行处理
            df = pd.DataFrame.from_dict(time_series, orient="index")
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # 根据时间范围筛选数据
            if range == "1m":
                df = df.last('30D')
            elif range == "3m":
                df = df.last('90D')
            elif range == "6m":
                df = df.last('180D')
            elif range == "1y":
                df = df.last('365D')
            
            # 重命名列
            df.columns = [col.split('. ')[1] for col in df.columns]
            
            # 转换为数值类型
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
            
            # 构建响应数据
            price_points = []
            for date, row in df.iterrows():
                price_point = StockPricePoint(
                    date=date.strftime('%Y-%m-%d'),
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=int(row['volume'])
                )
                price_points.append(price_point)
            
            return StockPriceHistory(symbol=symbol, data=price_points)
        except Exception as e:
            print(f"获取股票历史价格时出错: {str(e)}")
            return None
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """获取公司基本面数据"""
        try:
            # 调用 Alpha Vantage API
            params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            return data
        except Exception as e:
            print(f"获取基本面数据时出错: {str(e)}")
            return {}
    
    async def get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取股票历史数据"""
        try:
            # 调用 Alpha Vantage API
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "compact",
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            # 提取时间序列数据
            time_series_key = next((k for k in data.keys() if "Time Series" in k), None)
            if not time_series_key:
                return None
            
            time_series = data[time_series_key]
            
            # 转换为 DataFrame
            df = pd.DataFrame.from_dict(time_series, orient="index")
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # 重命名列
            df.columns = [col.split('. ')[1] for col in df.columns]
            
            # 转换为数值类型
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
            
            return df
        except Exception as e:
            print(f"获取历史数据时出错: {str(e)}")
            return None
    
    async def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """获取新闻情绪分析"""
        try:
            # 调用 Alpha Vantage API
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            return data
        except Exception as e:
            print(f"获取新闻情绪时出错: {str(e)}")
            return {} 