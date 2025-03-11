import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import random

from app.core.config import settings
from app.schemas.stock import AIAnalysis
from app.services.data_sources.factory import DataSourceFactory
from app.services.ml_service import MLService
from app.services.openai_service import OpenAIService

class AIService:
    """AI 分析服务，用于生成股票分析和建议"""
    
    # 分析模式映射
    _analysis_modes = {
        "rule": "_analyze_with_rule",
        "ml": "_analyze_with_ml",
        "llm": "_analyze_with_llm"
    }
    
    # 服务实例缓存
    _ml_service = None
    _openai_service = None
    
    @classmethod
    def get_ml_service(cls):
        """获取机器学习服务实例"""
        if cls._ml_service is None:
            cls._ml_service = MLService()
        return cls._ml_service
    
    @classmethod
    def get_openai_service(cls):
        """获取OpenAI服务实例"""
        if cls._openai_service is None:
            cls._openai_service = OpenAIService()
        return cls._openai_service
    
    @staticmethod
    async def analyze_stock(
        symbol: str, 
        data_source: str = None, 
        analysis_mode: str = None
    ) -> Optional[AIAnalysis]:
        """分析股票并生成 AI 建议"""
        try:
            # 如果未指定分析模式，使用默认模式
            if analysis_mode is None:
                analysis_mode = settings.DEFAULT_ANALYSIS_MODE
            
            # 如果分析模式无效，使用默认模式
            if analysis_mode not in AIService._analysis_modes:
                print(f"警告: 无效的分析模式 '{analysis_mode}'，使用默认模式 '{settings.DEFAULT_ANALYSIS_MODE}'")
                analysis_mode = settings.DEFAULT_ANALYSIS_MODE
            
            # 获取数据源
            ds = DataSourceFactory.get_data_source(data_source)
            
            # 获取股票历史数据
            historical_data = await ds.get_historical_data(symbol)
            if historical_data is None:
                return None
            
            # 获取股票信息
            stock_info = await ds.get_stock_info(symbol)
            if stock_info is None:
                return None
            
            # 获取公司基本面数据
            fundamentals = await ds.get_fundamentals(symbol)
            
            # 获取新闻情绪
            news_sentiment = await ds.get_news_sentiment(symbol)
            
            # 计算技术指标
            technical_indicators = AIService._calculate_technical_indicators(historical_data)
            
            # 根据分析模式调用相应的分析方法
            method_name = AIService._analysis_modes[analysis_mode]
            method = getattr(AIService, method_name)
            
            # 调用分析方法
            analysis = await method(
                symbol, 
                stock_info, 
                historical_data, 
                fundamentals, 
                news_sentiment,
                technical_indicators
            )
            
            return analysis
        except Exception as e:
            print(f"分析股票时出错: {str(e)}")
            return None
    
    @staticmethod
    async def _analyze_with_rule(
        symbol: str,
        stock_info: Dict[str, Any],
        historical_data: pd.DataFrame,
        fundamentals: Dict[str, Any],
        news_sentiment: Dict[str, Any],
        technical_indicators: Dict[str, float]
    ) -> AIAnalysis:
        """使用规则计算分析股票"""
        # 计算当前价格和变化
        current_price = historical_data['close'].iloc[-1]
        price_change = historical_data['close'].iloc[-1] - historical_data['close'].iloc[-2]
        price_change_percent = (price_change / historical_data['close'].iloc[-2]) * 100
        
        # 确定情绪
        sentiment = "neutral"
        if price_change_percent > 2:
            sentiment = "positive"
        elif price_change_percent < -2:
            sentiment = "negative"
        
        # 从新闻中提取情绪
        if 'feed' in news_sentiment and news_sentiment['feed']:
            news_sentiments = [
                float(article.get('overall_sentiment_score', 0)) 
                for article in news_sentiment['feed']
                if 'overall_sentiment_score' in article
            ]
            if news_sentiments:
                avg_news_sentiment = sum(news_sentiments) / len(news_sentiments)
                if avg_news_sentiment > 0.2:
                    sentiment = "positive"
                elif avg_news_sentiment < -0.2:
                    sentiment = "negative"
        
        # 生成关键点
        key_points = []
        
        # 技术指标关键点
        if current_price > technical_indicators['SMA_50']:
            key_points.append(f"价格高于50日均线，显示上升趋势")
        else:
            key_points.append(f"价格低于50日均线，可能处于下降趋势")
        
        if technical_indicators['RSI'] > 70:
            key_points.append(f"RSI为{technical_indicators['RSI']:.2f}，表明可能超买")
        elif technical_indicators['RSI'] < 30:
            key_points.append(f"RSI为{technical_indicators['RSI']:.2f}，表明可能超卖")
        else:
            key_points.append(f"RSI为{technical_indicators['RSI']:.2f}，处于中性区间")
        
        # 基本面关键点
        if fundamentals:
            pe_ratio = fundamentals.get('PERatio', 'N/A')
            if pe_ratio != 'N/A':
                try:
                    pe_ratio = float(pe_ratio)
                    if pe_ratio < 15:
                        key_points.append(f"市盈率为{pe_ratio:.2f}，相对较低")
                    elif pe_ratio > 30:
                        key_points.append(f"市盈率为{pe_ratio:.2f}，相对较高")
                    else:
                        key_points.append(f"市盈率为{pe_ratio:.2f}，处于合理范围")
                except (ValueError, TypeError):
                    pass
            
            dividend_yield = fundamentals.get('DividendYield', 'N/A')
            if dividend_yield != 'N/A' and dividend_yield != '0':
                try:
                    dividend_yield = float(dividend_yield) * 100
                    key_points.append(f"股息收益率为{dividend_yield:.2f}%")
                except (ValueError, TypeError):
                    pass
        
        # 确定风险水平
        risk_level = "medium"
        volatility = technical_indicators['Volatility'] / current_price * 100
        if volatility > 3:
            risk_level = "high"
        elif volatility < 1:
            risk_level = "low"
        
        # 生成建议
        if sentiment == "positive" and technical_indicators['RSI'] < 70:
            recommendation = "考虑买入或持有。技术指标和市场情绪都相对积极。"
        elif sentiment == "negative" and technical_indicators['RSI'] > 30:
            recommendation = "考虑减持或观望。技术指标和市场情绪相对消极。"
        else:
            recommendation = "持有并观察。市场信号不明确，建议等待更清晰的趋势。"
        
        # 生成摘要
        company_name = fundamentals.get('Name', symbol)
        summary = (
            f"{company_name}目前交易价格为{current_price:.2f}，"
            f"较前一交易日{price_change_percent:.2f}%。"
            f"基于技术分析和市场情绪，股票当前呈现{sentiment}态势。"
            f"风险水平评估为{risk_level}。"
        )
        
        return AIAnalysis(
            summary=summary,
            sentiment=sentiment,
            keyPoints=key_points,
            recommendation=recommendation,
            riskLevel=risk_level
        )
    
    @staticmethod
    async def _analyze_with_ml(
        symbol: str,
        stock_info: Dict[str, Any],
        historical_data: pd.DataFrame,
        fundamentals: Dict[str, Any],
        news_sentiment: Dict[str, Any],
        technical_indicators: Dict[str, float]
    ) -> AIAnalysis:
        """使用机器学习模型分析股票"""
        ml_service = AIService.get_ml_service()
        analysis = await ml_service.analyze_stock(
            symbol,
            historical_data,
            fundamentals,
            technical_indicators
        )
        
        # 如果机器学习分析失败，回退到规则分析
        if analysis is None:
            print("机器学习分析失败，回退到规则分析")
            return await AIService._analyze_with_rule(
                symbol,
                stock_info,
                historical_data,
                fundamentals,
                news_sentiment,
                technical_indicators
            )
        
        return analysis
    
    @staticmethod
    async def _analyze_with_llm(
        symbol: str,
        stock_info: Dict[str, Any],
        historical_data: pd.DataFrame,
        fundamentals: Dict[str, Any],
        news_sentiment: Dict[str, Any],
        technical_indicators: Dict[str, float]
    ) -> AIAnalysis:
        """使用大语言模型分析股票"""
        try:
            openai_service = AIService.get_openai_service()
            
            # 将 DataFrame 转换为字典
            historical_dict = {}
            for i, row in historical_data.tail(30).iterrows():
                date_str = i.strftime('%Y-%m-%d') if hasattr(i, 'strftime') else str(i)
                historical_dict[date_str] = {
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['volume']
                }
            
            # 将 stock_info 转换为字典
            stock_info_dict = {}
            if hasattr(stock_info, '__dict__'):
                stock_info_dict = stock_info.__dict__
            else:
                stock_info_dict = {
                    'symbol': symbol,
                    'name': getattr(stock_info, 'name', symbol),
                    'price': getattr(stock_info, 'price', historical_data['close'].iloc[-1]),
                    'changePercent': getattr(stock_info, 'changePercent', 0)
                }
            
            # 调用 OpenAI 服务
            result = await openai_service.analyze_stock(
                symbol,
                stock_info_dict,
                historical_dict,
                fundamentals,
                technical_indicators,
                news_sentiment
            )
            
            # 转换为 AIAnalysis 对象
            analysis = AIAnalysis(
                summary=result.get('summary', '无法生成分析'),
                sentiment=result.get('sentiment', 'neutral'),
                keyPoints=result.get('keyPoints', ['无法生成关键点']),
                recommendation=result.get('recommendation', '无法提供建议'),
                riskLevel=result.get('riskLevel', 'medium')
            )
            
            return analysis
        except Exception as e:
            print(f"大语言模型分析失败: {str(e)}，回退到规则分析")
            return await AIService._analyze_with_rule(
                symbol,
                stock_info,
                historical_data,
                fundamentals,
                news_sentiment,
                technical_indicators
            )
    
    @staticmethod
    def _calculate_technical_indicators(df: pd.DataFrame) -> Dict[str, float]:
        """计算技术指标"""
        indicators = {}
        
        # 计算移动平均线
        indicators['SMA_20'] = df['close'].rolling(window=20).mean().iloc[-1]
        indicators['SMA_50'] = df['close'].rolling(window=50).mean().iloc[-1]
        
        # 计算相对强弱指标 (RSI)
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        indicators['RSI'] = 100 - (100 / (1 + rs.iloc[-1]))
        
        # 计算波动率 (20日标准差)
        indicators['Volatility'] = df['close'].rolling(window=20).std().iloc[-1]
        
        # 计算MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        indicators['MACD'] = macd.iloc[-1]
        
        return indicators 