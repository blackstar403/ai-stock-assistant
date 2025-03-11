import tushare as ts
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta

from app.core.config import settings
from app.services.data_sources.base import DataSourceBase
from app.schemas.stock import StockInfo, StockPriceHistory, StockPricePoint

class TushareDataSource(DataSourceBase):
    """Tushare 数据源实现"""
    
    def __init__(self):
        # 初始化 Tushare
        self.api = ts.pro_api(settings.TUSHARE_API_TOKEN)
    
    async def search_stocks(self, query: str) -> List[StockInfo]:
        """搜索股票"""
        try:
            # 获取股票列表
            stocks = self.api.stock_basic(
                exchange='', 
                list_status='L', 
                fields='ts_code,name,exchange,curr_type'
            )
            
            # 过滤匹配的股票
            filtered_stocks = stocks[
                stocks['ts_code'].str.contains(query, case=False) | 
                stocks['name'].str.contains(query, case=False)
            ]
            
            results = []
            for _, row in filtered_stocks.iterrows():
                # 转换交易所代码
                exchange = "SSE" if row['exchange'] == "SSE" else "SZSE"
                
                stock_info = StockInfo(
                    symbol=row['ts_code'],
                    name=row['name'],
                    exchange=exchange,
                    currency=row['curr_type'] if 'curr_type' in row else 'CNY'
                )
                results.append(stock_info)
            
            return results[:10]  # 限制返回数量
        except Exception as e:
            print(f"搜索股票时出错: {str(e)}")
            return []
    
    async def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """获取股票详细信息"""
        try:
            # 获取股票基本信息
            stock_basic = self.api.stock_basic(
                ts_code=symbol, 
                fields='ts_code,name,exchange,curr_type,list_date'
            )
            
            if stock_basic.empty:
                return None
            
            # 获取最新行情
            today = datetime.now().strftime('%Y%m%d')
            daily = self.api.daily(ts_code=symbol, trade_date=today)
            
            # 如果当天没有数据，尝试获取最近的交易日数据
            if daily.empty:
                # 获取最近10个交易日
                trade_cal = self.api.trade_cal(
                    exchange='SSE', 
                    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
                    end_date=today
                )
                trade_dates = trade_cal[trade_cal['is_open'] == 1]['cal_date'].sort_values(ascending=False)
                
                for date in trade_dates:
                    daily = self.api.daily(ts_code=symbol, trade_date=date)
                    if not daily.empty:
                        break
            
            if daily.empty:
                return None
            
            # 获取公司基本信息
            company = self.api.stock_company(ts_code=symbol)
            
            # 构建股票信息
            row = stock_basic.iloc[0]
            daily_row = daily.iloc[0]
            
            # 计算涨跌幅
            change = daily_row['close'] - daily_row['pre_close']
            change_percent = (change / daily_row['pre_close']) * 100
            
            # 获取市值信息
            try:
                daily_basic = self.api.daily_basic(ts_code=symbol, trade_date=daily_row['trade_date'])
                market_cap = daily_basic.iloc[0]['total_mv'] * 10000 if not daily_basic.empty else 0
            except:
                market_cap = 0
            
            # 转换交易所代码
            exchange = "上海证券交易所" if row['exchange'] == "SSE" else "深圳证券交易所"
            
            stock_info = StockInfo(
                symbol=row['ts_code'],
                name=row['name'],
                exchange=exchange,
                currency='CNY',
                price=float(daily_row['close']),
                change=float(change),
                changePercent=float(change_percent),
                marketCap=float(market_cap),
                volume=int(daily_row['vol'] * 100)  # Tushare 成交量单位是手(100股)
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
            # 计算开始日期
            end_date = datetime.now()
            
            if range == "1m":
                start_date = end_date - timedelta(days=30)
            elif range == "3m":
                start_date = end_date - timedelta(days=90)
            elif range == "6m":
                start_date = end_date - timedelta(days=180)
            elif range == "1y":
                start_date = end_date - timedelta(days=365)
            else:  # 5y
                start_date = end_date - timedelta(days=365 * 5)
            
            # 格式化日期
            start_date_str = start_date.strftime('%Y%m%d')
            end_date_str = end_date.strftime('%Y%m%d')
            
            # 根据间隔选择 API
            if interval == "daily":
                df = self.api.daily(ts_code=symbol, start_date=start_date_str, end_date=end_date_str)
            elif interval == "weekly":
                df = self.api.weekly(ts_code=symbol, start_date=start_date_str, end_date=end_date_str)
            else:  # monthly
                df = self.api.monthly(ts_code=symbol, start_date=start_date_str, end_date=end_date_str)
            
            if df.empty:
                return None
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 构建响应数据
            price_points = []
            for _, row in df.iterrows():
                # 将日期从 YYYYMMDD 转换为 YYYY-MM-DD
                date_str = row['trade_date']
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                
                price_point = StockPricePoint(
                    date=formatted_date,
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['vol'] * 100)  # Tushare 成交量单位是手(100股)
                )
                price_points.append(price_point)
            
            return StockPriceHistory(symbol=symbol, data=price_points)
        except Exception as e:
            print(f"获取股票历史价格时出错: {str(e)}")
            return None
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """获取公司基本面数据"""
        try:
            # 获取公司基本信息
            company = self.api.stock_company(ts_code=symbol)
            
            # 获取财务指标
            today = datetime.now().strftime('%Y%m%d')
            fina_indicator = self.api.fina_indicator(ts_code=symbol, period=today[:6])
            
            # 如果当期没有数据，尝试获取最近的财报
            if fina_indicator.empty:
                # 尝试上一季度
                last_quarter = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
                fina_indicator = self.api.fina_indicator(ts_code=symbol, period=last_quarter[:6])
            
            # 获取最新行情
            daily_basic = self.api.daily_basic(ts_code=symbol, trade_date=today)
            
            # 如果当天没有数据，尝试获取最近的交易日数据
            if daily_basic.empty:
                # 获取最近10个交易日
                trade_cal = self.api.trade_cal(
                    exchange='SSE', 
                    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
                    end_date=today
                )
                trade_dates = trade_cal[trade_cal['is_open'] == 1]['cal_date'].sort_values(ascending=False)
                
                for date in trade_dates:
                    daily_basic = self.api.daily_basic(ts_code=symbol, trade_date=date)
                    if not daily_basic.empty:
                        break
            
            # 合并数据
            result = {}
            
            if not company.empty:
                company_row = company.iloc[0]
                for col in company.columns:
                    result[col] = company_row[col]
            
            if not fina_indicator.empty:
                fina_row = fina_indicator.iloc[0]
                for col in fina_indicator.columns:
                    result[f"fina_{col}"] = fina_row[col]
            
            if not daily_basic.empty:
                basic_row = daily_basic.iloc[0]
                for col in daily_basic.columns:
                    result[f"daily_{col}"] = basic_row[col]
            
            # 添加一些常用指标的映射，使其与 Alpha Vantage 格式兼容
            if not daily_basic.empty:
                basic_row = daily_basic.iloc[0]
                result["PERatio"] = basic_row["pe"] if "pe" in basic_row else "N/A"
                result["DividendYield"] = basic_row["dv_ratio"] / 100 if "dv_ratio" in basic_row else "0"
                result["MarketCapitalization"] = basic_row["total_mv"] * 10000 if "total_mv" in basic_row else 0
            
            return result
        except Exception as e:
            print(f"获取基本面数据时出错: {str(e)}")
            return {}
    
    async def get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取股票历史数据"""
        try:
            # 获取最近100个交易日的数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=150)).strftime('%Y%m%d')
            
            df = self.api.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
            
            if df.empty:
                return None
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 设置日期索引
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            df = df.set_index('trade_date')
            
            # 重命名列以匹配 Alpha Vantage 格式
            df = df.rename(columns={
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume'
            })
            
            # 转换成交量单位（手 -> 股）
            df['volume'] = df['volume'] * 100
            
            return df
        except Exception as e:
            print(f"获取历史数据时出错: {str(e)}")
            return None
    
    async def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """获取新闻情绪分析"""
        try:
            # Tushare 没有直接提供新闻情绪分析，返回一个空结果
            # 在实际应用中，可以考虑接入第三方新闻 API 或情感分析服务
            return {
                "feed": [],
                "sentiment_score_avg": 0
            }
        except Exception as e:
            print(f"获取新闻情绪时出错: {str(e)}")
            return {} 