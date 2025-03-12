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
        
        # 200日均线分析（根据《专业投机原理》，判断长期趋势）
        if technical_indicators['Price_vs_SMA200'] > 0:
            key_points.append(f"价格位于200日均线上方{technical_indicators['Price_vs_SMA200']*100:.2f}%，根据《专业投机原理》，处于长期上升趋势")
            long_term_trend = "上升"
        else:
            key_points.append(f"价格位于200日均线下方{abs(technical_indicators['Price_vs_SMA200'])*100:.2f}%，根据《专业投机原理》，处于长期下降趋势")
            long_term_trend = "下降"
        
        # 布林带分析
        bb_position = technical_indicators['BB_Position']
        if bb_position > 0.95:
            key_points.append(f"价格接近布林带上轨，可能处于超买状态，根据《专业投机原理》，考虑回调风险")
        elif bb_position < 0.05:
            key_points.append(f"价格接近布林带下轨，可能处于超卖状态，根据《专业投机原理》，可能出现反弹")
        
        # 布林带宽度分析
        if technical_indicators['BB_Width'] > 0.2:
            key_points.append(f"布林带宽度较大({technical_indicators['BB_Width']:.2f})，表明市场波动性高")
        elif technical_indicators['BB_Width'] < 0.05:
            key_points.append(f"布林带宽度较小({technical_indicators['BB_Width']:.2f})，表明市场波动性低，可能即将突破")
        
        # 技术指标关键点
        if current_price > technical_indicators['SMA_50']:
            key_points.append(f"价格高于50日均线，显示中期上升趋势")
        else:
            key_points.append(f"价格低于50日均线，可能处于中期下降趋势")
        
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
        
        # 生成建议（根据《专业投机原理》的趋势跟踪和反转策略）
        # 综合考虑200日均线（长期趋势）、布林带位置（短期超买超卖）和RSI
        
        # 长期趋势判断（200日均线）
        long_term_bullish = technical_indicators['Price_vs_SMA200'] > 0
        
        # 短期超买超卖判断（布林带位置）
        bb_position = technical_indicators['BB_Position']
        overbought = bb_position > 0.9 and technical_indicators['RSI'] > 70
        oversold = bb_position < 0.1 and technical_indicators['RSI'] < 30
        
        # 布林带收缩判断（可能突破）
        tight_bands = technical_indicators['BB_Width'] < 0.05
        
        if long_term_bullish:
            # 长期上升趋势
            if overbought:
                recommendation = "持有观望。价格处于长期上升趋势，但短期可能超买，根据《专业投机原理》，可考虑减仓或设置止盈。"
            elif oversold:
                recommendation = "考虑买入。价格处于长期上升趋势，且短期可能超卖，根据《专业投机原理》，这是较好的买入时机。"
            elif tight_bands:
                recommendation = "密切关注。布林带收缩，可能即将突破，在长期上升趋势中，突破方向可能向上，根据《专业投机原理》，可设置突破买入策略。"
            else:
                recommendation = "持有或小幅买入。价格处于长期上升趋势，根据《专业投机原理》的趋势跟踪策略，应跟随趋势操作。"
        else:
            # 长期下降趋势
            if overbought:
                recommendation = "考虑减仓。价格处于长期下降趋势，且短期可能超买，根据《专业投机原理》，这可能是减仓的好时机。"
            elif oversold:
                recommendation = "观望或小幅试探。价格处于长期下降趋势，虽短期可能超卖，但根据《专业投机原理》，不宜大量买入逆势品种。"
            elif tight_bands:
                recommendation = "密切关注。布林带收缩，可能即将突破，在长期下降趋势中，突破方向可能向下，根据《专业投机原理》，应保持谨慎。"
            else:
                recommendation = "观望或减仓。价格处于长期下降趋势，根据《专业投机原理》的趋势跟踪策略，应避免逆势操作。"
        
        # 生成摘要
        company_name = fundamentals.get('Name', symbol)
        summary = (
            f"{company_name}目前交易价格为{current_price:.2f}，"
            f"较前一交易日{price_change_percent:.2f}%。"
            f"基于技术分析和市场情绪，股票当前呈现{sentiment}态势。"
            f"长期趋势为{'上升' if long_term_bullish else '下降'}（200日均线），"
            f"布林带位置为{bb_position:.2f}（0-1，越接近1表示越接近上轨）。"
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
            
            # 增强技术指标信息，添加布林带和200日均线相关指标
            enhanced_technical_indicators = technical_indicators.copy()
            
            # 添加布林带和200日均线的解释信息
            enhanced_technical_indicators['BB_Description'] = (
                f"布林带: 上轨={technical_indicators['BB_Upper']:.2f}, "
                f"中轨={technical_indicators['BB_Middle']:.2f}, "
                f"下轨={technical_indicators['BB_Lower']:.2f}, "
                f"带宽={technical_indicators['BB_Width']:.2f}, "
                f"价格在带中位置={technical_indicators['BB_Position']:.2f} (0-1, 越接近1表示越接近上轨)"
            )
            
            enhanced_technical_indicators['SMA200_Description'] = (
                f"200日均线: {technical_indicators['SMA_200']:.2f}, "
                f"价格相对200日均线: {technical_indicators['Price_vs_SMA200']*100:.2f}% "
                f"({'高于' if technical_indicators['Price_vs_SMA200'] > 0 else '低于'}200日均线)"
            )
            
            # 添加《专业投机原理》的相关解释
            enhanced_technical_indicators['ProfessionalSpeculationPrinciples'] = (
                "根据《专业投机原理》，200日均线是判断长期趋势的重要指标，价格在200日均线之上视为多头市场，之下视为空头市场。"
                "布林带则用于判断短期超买超卖状态，价格接近上轨可能超买，接近下轨可能超卖。"
                "布林带收窄表示波动性降低，可能即将出现大幅突破行情。"
            )
            
            # 调用 OpenAI 服务
            result = await openai_service.analyze_stock(
                symbol,
                stock_info_dict,
                historical_dict,
                fundamentals,
                news_sentiment,
                enhanced_technical_indicators
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
        indicators['SMA_200'] = df['close'].rolling(window=200).mean().iloc[-1]

        # 计算200日均线相对位置（根据《专业投机原理》，判断长期趋势）
        current_price = df['close'].iloc[-1]
        indicators['Price_vs_SMA200'] = current_price / indicators['SMA_200'] - 1  # 正值表示价格在200日均线上方

        # 计算布林带指标 (Bollinger Bands)
        sma_20 = df['close'].rolling(window=99).mean()
        std_20 = df['close'].rolling(window=99).std()
        indicators['BB_Upper'] = (sma_20 + (std_20 * 2)).iloc[-1]  # 上轨（均线+2倍标准差）
        indicators['BB_Middle'] = sma_20.iloc[-1]  # 中轨（20日均线）
        indicators['BB_Lower'] = (sma_20 - (std_20 * 2)).iloc[-1]  # 下轨（均线-2倍标准差）
        indicators['BB_Width'] = (indicators['BB_Upper'] - indicators['BB_Lower']) / indicators['BB_Middle']  # 带宽
        indicators['BB_Position'] = (current_price - indicators['BB_Lower']) / (indicators['BB_Upper'] - indicators['BB_Lower'])  # 价格在带中的位置 (0-1)
        
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