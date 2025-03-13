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
        print(f"搜索股票: {query}")
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
            volume = int(float(row['成交量'])) * 100 if '成交量' in row and not pd.isna(row['成交量']) else 0
            
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
            print(stock_info)
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
        """获取新闻情绪分析和政策共振系数"""
        try:
            # 初始化结果
            result = {
                "feed": [],
                "sentiment_score_avg": 0,
                "policy_resonance": {
                    "coefficient": 0,
                    "policies": []
                }
            }
            
            # 获取股票相关新闻
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
                        
                        result["feed"] = feed
                except Exception as e:
                    print(f"获取股票新闻时出错: {str(e)}")
            
            # 获取政策新闻并计算政策共振系数
            try:
                # 获取最近的经济政策新闻
                policy_data = ak.news_economic_baidu()
                
                if not policy_data.empty:
                    # 获取股票名称
                    stock_name = ""
                    if code_match:
                        try:
                            stock_info = await self.get_stock_info(symbol)
                            if stock_info:
                                stock_name = stock_info.name
                        except:
                            pass
                    
                    # 计算政策共振系数
                    # 1. 提取最近30条政策新闻
                    recent_policies = policy_data.head(30)
                    
                    # 2. 初始化共振分数
                    resonance_score = 0
                    relevant_policies = []
                    
                    # 3. 分析每条政策新闻与股票的相关性
                    for _, policy in recent_policies.iterrows():
                        policy_title = policy.get("title", "")
                        policy_content = policy.get("content", "")
                        policy_date = policy.get("date", "")
                        
                        # 计算相关性分数 (简单的关键词匹配)
                        relevance = 0
                        
                        # 如果政策标题或内容包含股票名称，增加相关性
                        if stock_name and (stock_name in policy_title or stock_name in policy_content):
                            relevance += 3
                        
                        # 分析政策对行业的影响
                        industry_keywords = self._get_industry_keywords(symbol)
                        for keyword in industry_keywords:
                            if keyword in policy_title:
                                relevance += 2
                            elif keyword in policy_content:
                                relevance += 1
                        
                        # 如果政策相关，添加到相关政策列表
                        if relevance > 0:
                            resonance_score += relevance
                            relevant_policies.append({
                                "title": policy_title,
                                "date": policy_date,
                                "relevance": relevance,
                                "url": policy.get("url", "")
                            })
                    
                    # 4. 计算最终共振系数 (0-1之间)
                    if relevant_policies:
                        # 归一化共振分数 (最大可能分数为30条政策*最高相关性5=150)
                        normalized_score = min(1.0, resonance_score / 30)
                        result["policy_resonance"]["coefficient"] = normalized_score
                        result["policy_resonance"]["policies"] = relevant_policies[:5]  # 只返回最相关的5条
            
            except Exception as e:
                print(f"计算政策共振系数时出错: {str(e)}")
            
            return result
        except Exception as e:
            print(f"获取新闻情绪时出错: {str(e)}")
            return {
                "feed": [],
                "sentiment_score_avg": 0,
                "policy_resonance": {
                    "coefficient": 0,
                    "policies": []
                }
            }
    
    def _get_industry_keywords(self, symbol: str) -> List[str]:
        """获取股票所属行业的关键词"""
        try:
            # 从股票代码判断行业
            code_match = re.match(r'(\d+)\.([A-Z]+)', symbol)
            if not code_match:
                return []
            
            code = code_match.group(1)
            
            # 尝试获取股票所属行业
            try:
                stock_industry = ak.stock_industry_category_cninfo()
                stock_row = stock_industry[stock_industry['证券代码'] == code]
                
                if not stock_row.empty:
                    industry = stock_row.iloc[0]['所属行业']
                    # 根据行业返回相关关键词
                    return self._industry_to_keywords(industry)
            except:
                pass
            
            # 默认关键词
            return ["经济", "政策", "发展", "改革", "创新", "金融", "市场", "投资"]
        except:
            return ["经济", "政策", "发展", "改革", "创新", "金融", "市场", "投资"]
    
    def _industry_to_keywords(self, industry: str) -> List[str]:
        """根据行业返回相关关键词"""
        # 行业关键词映射
        industry_keywords = {
            "农业": ["农业", "种植", "农产品", "粮食", "农村", "乡村振兴"],
            "采矿业": ["矿业", "采矿", "矿产", "资源", "能源", "开采"],
            "制造业": ["制造", "工业", "生产", "加工", "工厂", "智能制造"],
            "电力": ["电力", "能源", "电网", "发电", "新能源", "碳中和"],
            "建筑业": ["建筑", "房地产", "基建", "工程", "城市建设"],
            "批发和零售业": ["零售", "商业", "消费", "电商", "商超", "贸易"],
            "交通运输": ["交通", "运输", "物流", "航运", "铁路", "公路"],
            "住宿和餐饮业": ["餐饮", "旅游", "酒店", "服务业", "消费"],
            "信息技术": ["科技", "互联网", "软件", "信息", "数字化", "人工智能", "大数据"],
            "金融业": ["金融", "银行", "保险", "证券", "投资", "理财"],
            "房地产业": ["房地产", "地产", "楼市", "住房", "建设"],
            "科学研究": ["科研", "研发", "创新", "技术", "专利"],
            "水利环境": ["环保", "水利", "生态", "环境", "可持续"],
            "居民服务": ["服务", "社区", "民生", "消费"],
            "教育": ["教育", "培训", "学校", "教学", "学习"],
            "卫生和社会工作": ["医疗", "卫生", "健康", "社会保障", "养老"],
            "文化体育娱乐业": ["文化", "体育", "娱乐", "传媒", "影视", "游戏"],
            "公共管理": ["公共", "管理", "政务", "行政"]
        }
        
        # 查找最匹配的行业
        for key, keywords in industry_keywords.items():
            if key in industry:
                return keywords + ["经济", "政策", "发展", "改革"]
        
        # 默认关键词
        return ["经济", "政策", "发展", "改革", "创新", "金融", "市场", "投资"]
    
    async def get_sector_linkage(self, symbol: str) -> Dict[str, Any]:
        """获取板块联动性分析"""
        try:
            # 解析股票代码
            code_match = re.match(r'(\d+)\.([A-Z]+)', symbol)
            if not code_match:
                return self._default_sector_linkage()
            
            code = code_match.group(1)
            
            # 获取股票所属板块
            try:
                # 获取股票行业分类数据
                stock_row = ak.stock_individual_info_em(symbol=code)

                # 提取行业信息
                industry_info = None
                for _, row in stock_row.iterrows():
                    if row['item'] == '行业':
                        industry_info = row['value']
                        break
                
                # 如果找不到行业信息，使用默认值
                if not industry_info:
                    return self._default_sector_linkage()
                
                # 设置行业名称
                sector_name = industry_info

                # 获取同行业股票
                sector_stocks = ak.stock_board_industry_cons_em(symbol=sector_name)
                sector_total = len(sector_stocks)
                
                if sector_total <= 1:
                    return self._default_sector_linkage(sector_name)
                
                # 获取板块内所有股票的历史数据
                sector_data = {}
                sector_codes = sector_stocks['代码'].tolist()
                
                # 限制处理的股票数量，避免请求过多
                max_stocks = min(20, len(sector_codes))
                sector_codes = sector_codes[:max_stocks]
                
                # 获取当前股票的历史数据
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
                
                target_stock_data = ak.stock_zh_a_hist(
                    symbol=code, 
                    period="daily", 
                    start_date=start_date, 
                    end_date=end_date, 
                    adjust="qfq"
                )
                
                if target_stock_data.empty:
                    return self._default_sector_linkage(sector_name)
                
                # 提取目标股票的收盘价序列
                target_stock_data['日期'] = pd.to_datetime(target_stock_data['日期'])
                target_stock_prices = target_stock_data.set_index('日期')['收盘']
                
                # 获取板块内其他股票的数据
                all_prices = {}
                for sector_code in sector_codes:
                    if sector_code == code:
                        all_prices[sector_code] = target_stock_prices
                        continue
                    
                    try:
                        stock_data = ak.stock_zh_a_hist(
                            symbol=sector_code, 
                            period="daily", 
                            start_date=start_date, 
                            end_date=end_date, 
                            adjust="qfq"
                        )
                        
                        if not stock_data.empty:
                            stock_data['日期'] = pd.to_datetime(stock_data['日期'])
                            all_prices[sector_code] = stock_data.set_index('日期')['收盘']
                    except:
                        continue
                
                # 计算相关性和带动性
                correlations = {}
                returns = {}
                
                # 计算每只股票的日收益率
                for code, prices in all_prices.items():
                    returns[code] = prices.pct_change().dropna()
                
                # 计算目标股票与其他股票的相关性
                target_returns = returns.get(code)
                if target_returns is None or len(target_returns) < 10:
                    return self._default_sector_linkage(sector_name)
                
                for other_code, other_returns in returns.items():
                    if other_code == code:
                        continue
                    
                    # 确保两个序列有相同的索引
                    common_idx = target_returns.index.intersection(other_returns.index)
                    if len(common_idx) < 10:
                        continue
                    
                    # 计算相关性
                    corr = target_returns.loc[common_idx].corr(other_returns.loc[common_idx])
                    correlations[other_code] = corr
                
                if not correlations:
                    return self._default_sector_linkage(sector_name)
                
                # 计算平均相关性
                avg_correlation = sum(correlations.values()) / len(correlations)
                
                # 计算带动性（使用格兰杰因果检验的简化版本）
                # 这里使用滞后相关性作为带动性的近似
                driving_force = 0
                
                # 计算目标股票对其他股票的滞后影响
                lag_influences = []
                for other_code, other_returns in returns.items():
                    if other_code == code:
                        continue
                    
                    # 确保两个序列有相同的索引
                    target_lagged = target_returns.shift(1).dropna()
                    common_idx = target_lagged.index.intersection(other_returns.index)
                    if len(common_idx) < 10:
                        continue
                    
                    # 计算滞后相关性
                    lag_corr = target_lagged.loc[common_idx].corr(other_returns.loc[common_idx])
                    lag_influences.append(max(0, lag_corr))  # 只考虑正向影响
                
                if lag_influences:
                    driving_force = sum(lag_influences) / len(lag_influences)
                
                # 计算板块内排名
                rank = 1
                for other_code in sector_codes:
                    if other_code == code:
                        continue
                    
                    try:
                        other_data = ak.stock_zh_a_hist(
                            symbol=other_code, 
                            period="daily", 
                            start_date=start_date, 
                            end_date=end_date, 
                            adjust="qfq"
                        )
                        
                        if not other_data.empty:
                            # 计算涨幅
                            other_return = (other_data['收盘'].iloc[-1] / other_data['收盘'].iloc[0] - 1) * 100
                            target_return = (target_stock_data['收盘'].iloc[-1] / target_stock_data['收盘'].iloc[0] - 1) * 100
                            
                            if other_return > target_return:
                                rank += 1
                    except:
                        continue
                
                # 返回结果
                return {
                    "sector_name": sector_name,
                    "correlation": float(min(1.0, max(0.0, avg_correlation))),  # 确保在0-1之间
                    "driving_force": float(min(1.0, max(0.0, driving_force * 2))),  # 放大并限制在0-1之间
                    "rank_in_sector": rank,
                    "total_in_sector": sector_total
                }
            
            except Exception as e:
                print(f"获取板块联动性时出错: {str(e)}")
                return self._default_sector_linkage()
        
        except Exception as e:
            print(f"获取板块联动性时出错: {str(e)}")
            return self._default_sector_linkage()
    
    def _default_sector_linkage(self, sector_name="未知板块") -> Dict[str, Any]:
        """返回默认的板块联动性数据"""
        return {
            "sector_name": sector_name,
            "correlation": 0.5,
            "driving_force": 0.3,
            "rank_in_sector": 0,
            "total_in_sector": 0
        }
    
    async def get_concept_distribution(self, symbol: str) -> Dict[str, Any]:
        """获取概念涨跌分布分析"""
        try:
            # 解析股票代码
            code_match = re.match(r'(\d+)\.([A-Z]+)', symbol)
            if not code_match:
                return self._default_concept_distribution()
            
            code = code_match.group(1)
            
            return self._default_concept_distribution()
            
            # 获取股票所属概念
            try:
                # 获取股票概念
                stock_concept = ak.stock_board_concept_name_em()

                if stock_concept.empty:
                    return self._default_concept_distribution()
                
                # 获取个股所属概念
                stock_concepts = []
                
                # 遍历概念，检查股票是否属于该概念
                for _, concept_row in stock_concept.iterrows():
                    concept_name = concept_row['板块名称']
                    concept_code = concept_row['板块代码']
                    try:
                        # 获取概念成分股
                        concept_stocks = ak.stock_board_concept_cons_em(symbol=concept_code)
                        # 检查股票是否在概念成分股中
                        if not concept_stocks.empty and code in concept_stocks['代码'].values:
                            # 获取概念指数
                            concept_index = ak.stock_board_concept_hist_ths(symbol=concept_code, period="D", start_date="20230101", end_date=datetime.now().strftime('%Y%m%d'))
                            
                            if not concept_index.empty:
                                # 计算概念强度（最近一个月的涨幅）
                                recent_data = concept_index.tail(20)  # 约一个月的交易日
                                if len(recent_data) > 5:
                                    concept_strength = (recent_data['收盘'].iloc[-1] / recent_data['收盘'].iloc[0] - 1)
                                    
                                    # 获取股票在概念中的排名
                                    rank = 1
                                    total = len(concept_stocks)
                                    
                                    # 获取个股最近一个月的涨幅
                                    end_date = datetime.now().strftime('%Y%m%d')
                                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
                                    
                                    stock_data = ak.stock_zh_a_hist(
                                        symbol=code, 
                                        period="daily", 
                                        start_date=start_date, 
                                        end_date=end_date, 
                                        adjust="qfq"
                                    )
                                    
                                    if not stock_data.empty and len(stock_data) > 5:
                                        stock_return = (stock_data['收盘'].iloc[-1] / stock_data['收盘'].iloc[0] - 1)
                                        
                                        # 计算股票在概念中的相对表现
                                        relative_performance = stock_return - concept_strength
                                        
                                        stock_concepts.append({
                                            "name": concept_name,
                                            "code": concept_code,
                                            "strength": float(min(1.0, max(-1.0, concept_strength))),  # 限制在-1到1之间
                                            "relative_performance": float(relative_performance),
                                            "rank": rank,  # 暂时设为1，后面会更新
                                            "total": total
                                        })
                    except:
                        continue
                
                if not stock_concepts:
                    return self._default_concept_distribution()
                
                # 计算概念整体强度
                concept_strengths = [c["strength"] for c in stock_concepts]
                overall_strength = sum([max(0, s) for s in concept_strengths]) / len(concept_strengths)
                
                # 按相对表现排序，找出领先和落后的概念
                stock_concepts.sort(key=lambda x: x["relative_performance"], reverse=True)
                
                leading_concepts = [c for c in stock_concepts if c["relative_performance"] > 0][:5]
                lagging_concepts = [c for c in stock_concepts if c["relative_performance"] < 0][-5:]
                lagging_concepts.reverse()  # 从小到大排序
                
                # 返回结果
                return {
                    "overall_strength": float(min(1.0, max(0.0, overall_strength))),  # 确保在0-1之间
                    "leading_concepts": leading_concepts,
                    "lagging_concepts": lagging_concepts,
                    "all_concepts": stock_concepts
                }
            
            except Exception as e:
                print(f"获取概念涨跌分布时出错: {str(e)}")
                return self._default_concept_distribution()
        
        except Exception as e:
            print(f"获取概念涨跌分布时出错: {str(e)}")
            return self._default_concept_distribution()
    
    def _default_concept_distribution(self) -> Dict[str, Any]:
        """返回默认的概念涨跌分布数据"""
        return {
            "overall_strength": 0.5,
            "leading_concepts": [],
            "lagging_concepts": [],
            "all_concepts": []
        }