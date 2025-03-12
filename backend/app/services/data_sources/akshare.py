import akshare as ak
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import re

from app.core.config import settings
from app.services.data_sources.base import DataSourceBase
from app.schemas.stock import StockInfo, StockPriceHistory, StockPricePoint

class AKShareDataSource(DataSourceBase):
    """AKShare 数据源实现"""
    
    def __init__(self):
        # 配置代理（如果需要）
        if settings.AKSHARE_USE_PROXY and settings.AKSHARE_PROXY_URL:
            ak.set_proxy(proxy=settings.AKSHARE_PROXY_URL)
    
    async def search_stocks(self, query: str) -> List[StockInfo]:
        """搜索股票"""
        try:
            # 获取A股股票列表
            stock_info_a_code_name_df = ak.stock_info_a_code_name()
            
            # 过滤匹配的股票
            filtered_stocks = stock_info_a_code_name_df[
                stock_info_a_code_name_df['code'].str.contains(query) | 
                stock_info_a_code_name_df['name'].str.contains(query)
            ]
            
            results = []
            for _, row in filtered_stocks.iterrows():
                # 判断交易所
                code = row['code']
                if code.startswith('6'):
                    exchange = "上海证券交易所"
                    symbol = f"{code}.SH"
                else:
                    exchange = "深圳证券交易所"
                    symbol = f"{code}.SZ"
                
                stock_info = StockInfo(
                    symbol=symbol,
                    name=row['name'],
                    exchange=exchange,
                    currency='CNY'
                )
                results.append(stock_info)
            
            return results[:10]  # 限制返回数量
        except Exception as e:
            print(f"搜索股票时出错: {str(e)}")
            return []
    
    async def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """获取股票详细信息"""
        try:
            # 解析股票代码
            code_match = re.match(r'(\d+)\.([A-Z]+)', symbol)
            if not code_match:
                return None
            
            code = code_match.group(1)
            market = code_match.group(2)
            
            # 获取实时行情
            if market == 'SH':
                df = ak.stock_sh_a_spot_em()
                df = df[df['代码'] == code]
            else:  # SZ
                df = ak.stock_sz_a_spot_em()
                df = df[df['代码'] == code]
            
            if df.empty:
                return None
            
            row = df.iloc[0]
            
            # 获取股票名称
            stock_info_df = ak.stock_info_a_code_name()
            stock_info = stock_info_df[stock_info_df['code'] == code]
            name = stock_info.iloc[0]['name'] if not stock_info.empty else ""
            
            # 确定交易所
            exchange = "上海证券交易所" if market == "SH" else "深圳证券交易所"
            
            # 计算涨跌幅
            price = float(row['最新价'])
            change = float(row['涨跌额'])
            change_percent = float(row['涨跌幅'])
            
            # 获取市值（亿元转为元）
            market_cap = float(row['总市值']) if '总市值' in row else 0
            
            # 获取成交量（手转为股）
            volume = int(row['成交量']) * 100 if '成交量' in row else 0
            
            stock_info = StockInfo(
                symbol=symbol,
                name=name,
                exchange=exchange,
                currency='CNY',
                price=price,
                change=change,
                changePercent=change_percent,
                marketCap=market_cap,
                volume=volume
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
            # 解析股票代码
            code_match = re.match(r'(\d+)\.([A-Z]+)', symbol)
            if not code_match:
                return None
            
            code = code_match.group(1)
            market = code_match.group(2)
            
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
            
            # 根据间隔选择不同的数据
            if interval == "daily":
                df = ak.stock_zh_a_hist(
                    symbol=code, 
                    period="daily", 
                    start_date=start_date_str, 
                    end_date=end_date_str, 
                    adjust="qfq"
                )
            elif interval == "weekly":
                df = ak.stock_zh_a_hist(
                    symbol=code, 
                    period="weekly", 
                    start_date=start_date_str, 
                    end_date=end_date_str, 
                    adjust="qfq"
                )
            else:  # monthly
                df = ak.stock_zh_a_hist(
                    symbol=code, 
                    period="monthly", 
                    start_date=start_date_str, 
                    end_date=end_date_str, 
                    adjust="qfq"
                )
            
            if df.empty:
                return None
            
            # 构建响应数据
            price_points = []
            for _, row in df.iterrows():
                # 将日期转换为字符串格式
                date_str = row['日期']
                if isinstance(date_str, datetime):
                    date_str = date_str.strftime('%Y-%m-%d')
                elif isinstance(date_str, pd.Timestamp):
                    date_str = date_str.strftime('%Y-%m-%d')
                elif isinstance(date_str, str):
                    date_str = date_str
                else:
                    date_str = str(date_str)
                
                price_point = StockPricePoint(
                    date=date_str,
                    open=float(row['开盘']),
                    high=float(row['最高']),
                    low=float(row['最低']),
                    close=float(row['收盘']),
                    volume=int(row['成交量'])
                )
                price_points.append(price_point)
            
            return StockPriceHistory(symbol=symbol, data=price_points)
        except Exception as e:
            print(f"获取股票历史价格时出错: {str(e)}")
            return None
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """获取公司基本面数据"""
        try:
            # 解析股票代码
            code_match = re.match(r'(\d+)\.([A-Z]+)', symbol)
            if not code_match:
                return {}
            
            code = code_match.group(1)
            
            # 获取公司基本信息
            stock_info = ak.stock_individual_info_em(symbol=code)
            
            # 获取财务指标
            financial_indicator = ak.stock_financial_analysis_indicator(symbol=code)
            
            # 获取市盈率、市净率等指标
            stock_a_lg_indicator = ak.stock_a_indicator_lg(symbol=code)
            
            # 合并数据
            result = {}
            
            # 处理公司基本信息
            if not stock_info.empty:
                for _, row in stock_info.iterrows():
                    result[row.iloc[0]] = row.iloc[1]
            
            # 处理最新的财务指标
            if not financial_indicator.empty:
                latest_financial = financial_indicator.iloc[0]
                for col in financial_indicator.columns:
                    result[f"fin_{col}"] = latest_financial[col]
            
            # 处理市场指标
            if not stock_a_lg_indicator.empty:
                latest_indicator = stock_a_lg_indicator.iloc[0]
                for col in stock_a_lg_indicator.columns:
                    result[f"ind_{col}"] = latest_indicator[col]
            
            # 添加一些常用指标的映射，使其与 Alpha Vantage 格式兼容
            if not stock_a_lg_indicator.empty:
                latest_indicator = stock_a_lg_indicator.iloc[0]
                result["PERatio"] = latest_indicator["pe"] if "pe" in latest_indicator else "N/A"
                result["PBRatio"] = latest_indicator["pb"] if "pb" in latest_indicator else "N/A"
            
            # 获取股息率
            try:
                dividend_info = ak.stock_history_dividend_detail(symbol=code, indicator="分红")
                if not dividend_info.empty:
                    latest_dividend = dividend_info.iloc[0]
                    result["DividendYield"] = latest_dividend["派息比例"] if "派息比例" in latest_dividend else "0"
                else:
                    result["DividendYield"] = "0"
            except:
                result["DividendYield"] = "0"
            
            # 获取市值
            try:
                stock_zh_a_spot_em = ak.stock_zh_a_spot_em()
                stock_info = stock_zh_a_spot_em[stock_zh_a_spot_em['代码'] == code]
                if not stock_info.empty:
                    result["MarketCapitalization"] = float(stock_info.iloc[0]['总市值']) * 100000000
                else:
                    result["MarketCapitalization"] = 0
            except:
                result["MarketCapitalization"] = 0
            
            return result
        except Exception as e:
            print(f"获取基本面数据时出错: {str(e)}")
            return {}
    
    async def get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取股票历史数据"""
        try:
            # 解析股票代码
            code_match = re.match(r'(\d+)\.([A-Z]+)', symbol)
            if not code_match:
                return None
            
            code = code_match.group(1)
            
            # 获取最近100个交易日的数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(
                symbol=code, 
                period="daily", 
                start_date=start_date, 
                end_date=end_date, 
                adjust="qfq"
            )
            print(f"获取历史数据: {len(df)}")
            
            if df.empty:
                return None
            
            # 设置日期索引
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.set_index('日期')
            
            # 重命名列以匹配 Alpha Vantage 格式
            df = df.rename(columns={
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            })
            
            return df
        except Exception as e:
            print(f"获取历史数据时出错: {str(e)}")
            return None
    
    async def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """获取新闻情绪分析"""
        try:
            # AKShare 没有直接提供新闻情绪分析，返回一个空结果
            # 在实际应用中，可以考虑接入第三方新闻 API 或情感分析服务
            
            # 尝试获取一些相关新闻
            code_match = re.match(r'(\d+)\.([A-Z]+)', symbol)
            if code_match:
                code = code_match.group(1)
                try:
                    # 获取股票相关新闻
                    stock_news = ak.stock_news_em(symbol=code)
                    
                    if not stock_news.empty:
                        feed = []
                        for _, row in stock_news.iterrows():
                            feed.append({
                                "title": row["新闻标题"] if "新闻标题" in row else "",
                                "url": row["新闻链接"] if "新闻链接" in row else "",
                                "time_published": row["发布时间"] if "发布时间" in row else "",
                                "overall_sentiment_score": 0  # 没有情感分析，默认为中性
                            })
                        
                        return {
                            "feed": feed,
                            "sentiment_score_avg": 0
                        }
                except:
                    pass
            
            return {
                "feed": [],
                "sentiment_score_avg": 0
            }
        except Exception as e:
            print(f"获取新闻情绪时出错: {str(e)}")
            return {}