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
            print(f"获取股票历史数据: {symbol}")
            historical_data = await ds.get_historical_data(symbol)
            if historical_data is None:
                return None
            
            # 获取股票信息
            print(f"获取股票信息: {symbol}")
            stock_info = await ds.get_stock_info(symbol)
            if stock_info is None:
                return None
            
            # 获取公司基本面数据
            print(f"获取公司基本面数据: {symbol}")
            fundamentals = await ds.get_fundamentals(symbol)
            
            # 获取新闻情绪
            print(f"获取新闻情绪: {symbol}")
            news_sentiment = await ds.get_news_sentiment(symbol)
            
            # 获取板块联动性和概念涨跌分布
            print(f"获取板块联动性和概念涨跌分布: {symbol}")
            sector_linkage = await ds.get_sector_linkage(symbol)
            concept_distribution = await ds.get_concept_distribution(symbol)
            
            # 计算技术指标
            print(f"计算技术指标: {symbol}")
            technical_indicators = AIService._calculate_technical_indicators(historical_data)
            
            # 根据分析模式调用相应的分析方法
            print(f"分析模式: {analysis_mode}")
            method_name = AIService._analysis_modes[analysis_mode]
            method = getattr(AIService, method_name)
            
            # 调用分析方法
            analysis = await method(
                symbol, 
                stock_info, 
                historical_data, 
                fundamentals, 
                news_sentiment,
                sector_linkage,
                concept_distribution,
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
        sector_linkage: Dict[str, Any],
        concept_distribution: Dict[str, Any],
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
        
        # 板块联动性分析
        sector_driving_force = sector_linkage.get('driving_force', 0)
        sector_correlation = sector_linkage.get('correlation', 0)
        sector_name = sector_linkage.get('sector_name', '未知板块')
        sector_rank = sector_linkage.get('rank_in_sector', 0)
        sector_total = sector_linkage.get('total_in_sector', 0)
        
        # 板块地位分析
        if sector_driving_force > 0.7:
            key_points.append(f"该股在{sector_name}板块中具有较强带动性(驱动力:{sector_driving_force:.2f})，为板块龙头股")
            if sector_rank <= 3 and sector_total > 0:
                key_points.append(f"在{sector_name}板块中排名第{sector_rank}/{sector_total}，处于领先地位")
        elif sector_driving_force > 0.4:
            key_points.append(f"该股在{sector_name}板块中具有一定带动性(驱动力:{sector_driving_force:.2f})，为板块重要成员")
        else:
            key_points.append(f"该股在{sector_name}板块中带动性较弱(驱动力:{sector_driving_force:.2f})，主要跟随板块整体走势")
        
        # 板块联动性分析
        if sector_correlation > 0.8:
            key_points.append(f"与{sector_name}板块联动性极强(相关性:{sector_correlation:.2f})，高度同步波动")
        elif sector_correlation > 0.5:
            key_points.append(f"与{sector_name}板块联动性较强(相关性:{sector_correlation:.2f})，整体同步波动")
        else:
            key_points.append(f"与{sector_name}板块联动性较弱(相关性:{sector_correlation:.2f})，存在独立行情可能")
        
        # 概念涨跌分布分析
        concept_strength = concept_distribution.get('overall_strength', 0)
        leading_concepts = concept_distribution.get('leading_concepts', [])
        lagging_concepts = concept_distribution.get('lagging_concepts', [])
        
        # 概念强度分析
        if concept_strength > 0.7:
            key_points.append(f"所属概念整体强势(强度:{concept_strength:.2f})，概念板块支撑较强")
            if leading_concepts:
                concepts_str = '、'.join([c.get('name', '') for c in leading_concepts[:2]])
                key_points.append(f"在{concepts_str}等概念中表现活跃，具有较强主动性")
        elif concept_strength > 0.4:
            key_points.append(f"所属概念中性偏强(强度:{concept_strength:.2f})，概念板块支撑一般")
        else:
            key_points.append(f"所属概念整体弱势(强度:{concept_strength:.2f})，概念板块支撑较弱")
            if lagging_concepts:
                concepts_str = '、'.join([c.get('name', '') for c in lagging_concepts[:2]])
                key_points.append(f"在{concepts_str}等概念中表现落后，缺乏主动性")
        
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
        
        # 政策共振分析
        policy_resonance = news_sentiment.get('policy_resonance', {})
        policy_coefficient = policy_resonance.get('coefficient', 0)
        relevant_policies = policy_resonance.get('policies', [])
        
        if policy_coefficient > 0:
            if policy_coefficient > 0.7:
                key_points.append(f"政策共振系数较高({policy_coefficient:.2f})，表明该股票与近期政策高度相关")
                if relevant_policies:
                    policy_titles = [p.get('title', '') for p in relevant_policies[:2]]
                    key_points.append(f"相关政策: {', '.join(policy_titles)}")
            elif policy_coefficient > 0.3:
                key_points.append(f"政策共振系数中等({policy_coefficient:.2f})，表明该股票受近期政策影响")
            else:
                key_points.append(f"政策共振系数较低({policy_coefficient:.2f})，表明该股票与近期政策关联度不高")
        
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
        
        # 政策风险调整
        if policy_coefficient > 0.5:
            # 政策共振高时，根据政策性质调整风险
            if long_term_trend == "上升":
                # 上升趋势中的高政策共振可能是利好，降低风险
                if risk_level == "high":
                    risk_level = "medium"
            else:
                # 下降趋势中的高政策共振可能是利空，提高风险
                if risk_level == "low":
                    risk_level = "medium"
        
        # 板块联动性风险调整
        if sector_driving_force > 0.6:
            # 高带动性股票风险可能更高，因为波动更大
            if risk_level == "low":
                risk_level = "medium"
        elif sector_correlation > 0.8 and concept_strength < 0.3:
            # 高联动性但概念弱势，风险可能更高
            if risk_level == "low":
                risk_level = "medium"
        
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
        
        # 政策因素
        policy_bullish = policy_coefficient > 0.5
        
        # 板块和概念因素
        sector_bullish = sector_driving_force > 0.5 or (sector_correlation > 0.7 and concept_strength > 0.6)
        
        # 综合建议
        if long_term_bullish:
            # 长期上升趋势
            if overbought:
                if policy_bullish and sector_bullish:
                    recommendation = "持有观望。价格处于长期上升趋势，虽短期可能超买，但政策共振较强且板块地位突出，可继续持有并设置止盈。"
                elif policy_bullish:
                    recommendation = "持有观望。价格处于长期上升趋势，虽短期可能超买，但政策共振较强，可继续持有并设置止盈。"
                elif sector_bullish:
                    recommendation = "持有观望。价格处于长期上升趋势，虽短期可能超买，但在板块中具有较强带动性，可持有并设置止盈。"
                else:
                    recommendation = "持有观望。价格处于长期上升趋势，但短期可能超买，根据《专业投机原理》，可考虑减仓或设置止盈。"
            elif oversold:
                if policy_bullish and sector_bullish:
                    recommendation = "积极买入。价格处于长期上升趋势，且短期可能超卖，政策共振较强且板块地位突出，这是较好的买入时机。"
                elif policy_bullish:
                    recommendation = "积极买入。价格处于长期上升趋势，且短期可能超卖，政策共振较强，可根据《专业投机原理》的趋势跟踪策略，这是较好的买入时机。"
                elif sector_bullish:
                    recommendation = "考虑买入。价格处于长期上升趋势，且短期可能超卖，在板块中具有较强带动性，可适量买入。"
                else:
                    recommendation = "考虑买入。价格处于长期上升趋势，且短期可能超卖，可根据《专业投机原理》的趋势跟踪策略，这是较好的买入时机。"
            elif tight_bands:
                if sector_driving_force > 0.7:
                    recommendation = "密切关注。布林带收缩，可能即将突破，在长期上升趋势中且具有较强板块带动性，突破方向可能向上，可设置突破买入策略。"
                else:
                    recommendation = "密切关注。布林带收缩，可能即将突破，在长期上升趋势中，突破方向可能向上，可根据《专业投机原理》的趋势跟踪策略，可设置突破买入策略。"
            else:
                if policy_bullish and sector_bullish:
                    recommendation = "持有或适量买入。价格处于长期上升趋势，政策共振较强且板块地位突出，应跟随趋势操作。"
                elif policy_bullish:
                    recommendation = "持有或适量买入。价格处于长期上升趋势，政策共振较强，可根据《专业投机原理》的趋势跟踪策略，应跟随趋势操作。"
                elif sector_bullish:
                    recommendation = "持有或小幅买入。价格处于长期上升趋势，在板块中具有较强地位，可跟随趋势操作。"
                else:
                    recommendation = "持有或小幅买入。价格处于长期上升趋势，可根据《专业投机原理》的趋势跟踪策略，应跟随趋势操作。"
        else:
            # 长期下降趋势
            if overbought:
                if sector_driving_force > 0.7:
                    recommendation = "谨慎持有。价格处于长期下降趋势，但短期可能超买，且在板块中具有较强带动性，可能出现独立行情。"
                else:
                    recommendation = "考虑减仓。价格处于长期下降趋势，且短期可能超买，可根据专业投机原理》，这可能是减仓的好时机。"
            elif oversold:
                if policy_bullish and sector_bullish:
                    recommendation = "观望或试探性买入。价格处于长期下降趋势，但短期可能超卖，且政策共振较强和板块地位突出，可小仓位试探。"
                elif policy_bullish:
                    recommendation = "观望或试探性买入。价格处于长期下降趋势，但短期可能超卖，且政策共振较强，可根据《专业投机原理》的趋势跟踪策略，可小仓位试探。"
                elif sector_bullish:
                    recommendation = "观望或小幅试探。价格处于长期下降趋势，虽短期可能超卖，但在板块中具有一定地位，可少量试探。"
                else:
                    recommendation = "观望或小幅试探。价格处于长期下降趋势，虽短期可能超卖，但可根据《专业投机原理》的趋势跟踪策略，不宜大量买入逆势品种。"
            elif tight_bands:
                if sector_driving_force > 0.7:
                    recommendation = "密切关注。布林带收缩，可能即将突破，虽处于长期下降趋势，但在板块中具有较强带动性，可能出现独立行情。"
                else:
                    recommendation = "密切关注。布林带收缩，可能即将突破，在长期下降趋势中，突破方向可能向下，可根据《专业投机原理》的趋势跟踪策略，应保持谨慎。"
            else:
                if policy_bullish and sector_bullish:
                    recommendation = "观望。价格处于长期下降趋势，但政策共振较强且板块地位突出，可等待趋势转变信号。"
                elif policy_bullish:
                    recommendation = "观望。价格处于长期下降趋势，但政策共振较强，可根据《专业投机原理》的趋势跟踪策略，可等待趋势转变信号。"
                elif sector_bullish:
                    recommendation = "观望。价格处于长期下降趋势，但在板块中具有一定地位，可等待板块整体转强信号。"
                else:
                    recommendation = "观望或减仓。价格处于长期下降趋势，可根据《专业投机原理》的趋势跟踪策略，应避免逆势操作。"
        
        # 生成摘要
        company_name = fundamentals.get('Name', symbol)
        summary = (
            f"{company_name}目前交易价格为{current_price:.2f}，"
            f"较前一交易日{price_change_percent:.2f}%。"
            f"基于技术分析和市场情绪，股票当前呈现{sentiment}态势。"
            f"长期趋势为{'上升' if long_term_bullish else '下降'}（200日均线），"
            f"布林带位置为{bb_position:.2f}（0-1，越接近1表示越接近上轨）。"
        )
        
        # 添加板块和概念信息
        summary += f"在{sector_name}板块中"
        if sector_driving_force > 0.7:
            summary += f"具有较强带动性(驱动力:{sector_driving_force:.2f})，为板块龙头股。"
        elif sector_driving_force > 0.4:
            summary += f"具有一定带动性(驱动力:{sector_driving_force:.2f})。"
        else:
            summary += f"带动性较弱(驱动力:{sector_driving_force:.2f})。"
        
        if concept_strength > 0.6:
            summary += f"所属概念整体较强(强度:{concept_strength:.2f})。"
        else:
            summary += f"所属概念整体较弱(强度:{concept_strength:.2f})。"
        
        # 添加政策共振信息
        if policy_coefficient > 0:
            summary += f"政策共振系数为{policy_coefficient:.2f}，"
            if policy_coefficient > 0.7:
                summary += "与近期政策高度相关。"
            elif policy_coefficient > 0.3:
                summary += "与近期政策有一定关联。"
            else:
                summary += "与近期政策关联度较低。"
        
        summary += f"风险水平评估为{risk_level}。"
        
        return AIAnalysis(
            summary=summary,
            sentiment=sentiment,
            keyPoints=key_points,
            recommendation=recommendation,
            riskLevel=risk_level,
            analysisType="rule"
        )
    
    @staticmethod
    async def _analyze_with_ml(
        symbol: str,
        stock_info: Dict[str, Any],
        historical_data: pd.DataFrame,
        fundamentals: Dict[str, Any],
        news_sentiment: Dict[str, Any],
        sector_linkage: Dict[str, Any],
        concept_distribution: Dict[str, Any],
        technical_indicators: Dict[str, float]
    ) -> AIAnalysis:
        """使用机器学习模型分析股票"""
        ml_service = AIService.get_ml_service()
        analysis = await ml_service.analyze_stock(
            symbol,
            historical_data,
            fundamentals,
            technical_indicators,
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
                sector_linkage,
                concept_distribution,
                technical_indicators
            )
        
        # 添加分析类型
        analysis.analysisType = "ml"
        return analysis
    
    @staticmethod
    async def _analyze_with_llm(
        symbol: str,
        stock_info: Dict[str, Any],
        historical_data: pd.DataFrame,
        fundamentals: Dict[str, Any],
        news_sentiment: Dict[str, Any],
        sector_linkage: Dict[str, Any],
        concept_distribution: Dict[str, Any],
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
                "政策共振系数反映股票与近期政策的关联度，高共振系数表明股票可能受政策影响较大。"
                "板块联动性和概念涨跌分布反映个股在板块中的地位和主动性，高带动性表明个股可能引领板块走势。"
            )
            
            # 确保news_sentiment包含policy_resonance字段
            if 'policy_resonance' not in news_sentiment:
                news_sentiment['policy_resonance'] = {
                    'coefficient': 0,
                    'policies': []
                }
            
            # 调用 OpenAI 服务
            result = await openai_service.analyze_stock(
                symbol,
                stock_info_dict,
                historical_dict,
                fundamentals,
                news_sentiment,
                sector_linkage,
                concept_distribution,
                enhanced_technical_indicators
            )
            
            # 转换为 AIAnalysis 对象
            analysis = AIAnalysis(
                summary=result.get('summary', '无法生成分析'),
                sentiment=result.get('sentiment', 'neutral'),
                keyPoints=result.get('keyPoints', ['无法生成关键点']),
                recommendation=result.get('recommendation', '无法提供建议'),
                riskLevel=result.get('riskLevel', 'medium'),
                analysisType="llm"
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
                sector_linkage,
                concept_distribution,
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
        sma_20 = df['close'].rolling(window=25).mean() # 25日均线
        std_20 = df['close'].rolling(window=25).std() # 25日均线标准差
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

    @staticmethod
    async def analyze_time_series(
        symbol: str,
        interval: str = "daily",
        range: str = "1m",
        data_source: str = None,
        analysis_mode: str = None
    ) -> Optional[Dict[str, Any]]:
        """分析股票分时数据并生成 AI 预测和分析"""
        try:
            # 如果未指定分析模式，使用默认模式
            if analysis_mode is None:
                analysis_mode = settings.DEFAULT_ANALYSIS_MODE
                
            # 获取数据源
            data_source_instance = DataSourceFactory.get_data_source(data_source)
            
            # 获取股票信息
            stock_info = await data_source_instance.get_stock_info(symbol)
            if not stock_info:
                return None
                
            # 获取历史价格数据
            price_history = await data_source_instance.get_stock_price_history(symbol, interval, range)
            if not price_history or not price_history.data or len(price_history.data) == 0:
                return None
                
            # 转换为 pandas DataFrame 进行分析
            historical_data = pd.DataFrame([
                {
                    'date': point.date,
                    'open': point.open,
                    'high': point.high,
                    'low': point.low,
                    'close': point.close,
                    'volume': point.volume
                }
                for point in price_history.data
            ])
            
            # 计算技术指标
            technical_indicators = AIService._calculate_technical_indicators(historical_data)
            
            # 根据分析模式选择分析方法
            if analysis_mode == "rule":
                time_series_analysis = await AIService._analyze_time_series_with_rule(historical_data, technical_indicators)
            elif analysis_mode == "ml":
                time_series_analysis = await AIService._analyze_time_series_with_ml(symbol, historical_data, technical_indicators)
            elif analysis_mode == "llm":
                time_series_analysis = await AIService._analyze_time_series_with_llm(symbol, stock_info, historical_data, technical_indicators)
            else:
                # 默认使用规则分析
                time_series_analysis = await AIService._analyze_time_series_with_rule(historical_data, technical_indicators)
                
            return time_series_analysis
            
        except Exception as e:
            print(f"Error analyzing time series for {symbol}: {str(e)}")
            return None
            
    @staticmethod
    async def _analyze_time_series_with_rule(
        historical_data: pd.DataFrame,
        technical_indicators: Dict[str, float]
    ) -> Dict[str, Any]:
        """使用规则分析分时数据"""
        # 确保数据按日期排序
        historical_data = historical_data.sort_values('date')
        
        # 计算移动平均线
        historical_data['ma5'] = historical_data['close'].rolling(window=5).mean()
        historical_data['ma10'] = historical_data['close'].rolling(window=10).mean()
        historical_data['ma20'] = historical_data['close'].rolling(window=20).mean()
        
        # 计算MACD
        exp1 = historical_data['close'].ewm(span=12, adjust=False).mean()
        exp2 = historical_data['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        # 获取最新数据
        latest_data = historical_data.iloc[-1]
        
        # 预测未来5个交易日的价格趋势
        price_trend = []
        last_close = latest_data['close']
        
        # 简单线性预测
        for i in range(1, 6):
            # 使用简单的线性回归预测
            if len(historical_data) >= 5:
                recent_data = historical_data.tail(5)
                avg_change = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / 4
                predicted_price = last_close + (avg_change * i)
                price_trend.append({
                    'day': i,
                    'predicted_price': round(float(predicted_price), 2)
                })
        
        # 生成支撑位和阻力位
        support_levels = []
        resistance_levels = []
        
        # 简单方法：使用最近低点作为支撑位，最近高点作为阻力位
        if len(historical_data) >= 10:
            recent_data = historical_data.tail(10)
            min_price = recent_data['low'].min()
            max_price = recent_data['high'].max()
            
            # 添加支撑位
            support_levels.append(round(float(min_price), 2))
            support_levels.append(round(float(min_price * 0.98), 2))
            
            # 添加阻力位
            resistance_levels.append(round(float(max_price), 2))
            resistance_levels.append(round(float(max_price * 1.02), 2))
        
        # 生成分析结果
        result = {
            'prediction': {
                'price_trend': price_trend,
                'support_levels': support_levels,
                'resistance_levels': resistance_levels
            },
            'indicators': {
                'ma5': round(float(latest_data['ma5'] if not pd.isna(latest_data['ma5']) else 0), 2),
                'ma10': round(float(latest_data['ma10'] if not pd.isna(latest_data['ma10']) else 0), 2),
                'ma20': round(float(latest_data['ma20'] if not pd.isna(latest_data['ma20']) else 0), 2),
                'macd': round(float(macd.iloc[-1]), 2),
                'signal': round(float(signal.iloc[-1]), 2),
                'histogram': round(float(hist.iloc[-1]), 2)
            },
            'analysis': {
                'trend': 'bullish' if technical_indicators.get('rsi', 50) > 50 else 'bearish',
                'strength': 'strong' if abs(technical_indicators.get('rsi', 50) - 50) > 15 else 'weak',
                'summary': f"{'看涨' if technical_indicators.get('rsi', 50) > 50 else '看跌'}趋势，{'强' if abs(technical_indicators.get('rsi', 50) - 50) > 15 else '弱'}势。"
            }
        }
        
        return result
        
    @staticmethod
    async def _analyze_time_series_with_ml(
        symbol: str,
        historical_data: pd.DataFrame,
        technical_indicators: Dict[str, float]
    ) -> Dict[str, Any]:
        """使用机器学习分析分时数据"""
        # 获取ML服务实例
        ml_service = AIService.get_ml_service()
        
        # 确保数据按日期排序
        historical_data = historical_data.sort_values('date')
        
        # 使用ML模型预测未来价格
        try:
            # 准备特征
            features = historical_data[['open', 'high', 'low', 'close', 'volume']].copy()
            
            # 添加技术指标作为特征
            for indicator, value in technical_indicators.items():
                features[indicator] = value
                
            # 预测未来5个交易日的价格
            predictions = ml_service.predict_time_series(features, days=5)
            
            # 格式化预测结果
            price_trend = []
            for i, price in enumerate(predictions):
                price_trend.append({
                    'day': i + 1,
                    'predicted_price': round(float(price), 2)
                })
                
            # 计算支撑位和阻力位
            support_level = round(float(min(predictions) * 0.98), 2)
            resistance_level = round(float(max(predictions) * 1.02), 2)
            
            # 生成分析结果
            result = {
                'prediction': {
                    'price_trend': price_trend,
                    'support_levels': [support_level],
                    'resistance_levels': [resistance_level]
                },
                'indicators': technical_indicators,
                'analysis': {
                    'trend': 'bullish' if predictions[-1] > historical_data['close'].iloc[-1] else 'bearish',
                    'strength': 'strong' if abs(predictions[-1] - historical_data['close'].iloc[-1]) / historical_data['close'].iloc[-1] > 0.02 else 'weak',
                    'summary': f"ML模型预测{'看涨' if predictions[-1] > historical_data['close'].iloc[-1] else '看跌'}趋势，{'强' if abs(predictions[-1] - historical_data['close'].iloc[-1]) / historical_data['close'].iloc[-1] > 0.02 else '弱'}势。"
                }
            }
            
            return result
            
        except Exception as e:
            print(f"Error in ML time series analysis: {str(e)}")
            # 如果ML分析失败，回退到规则分析
            return await AIService._analyze_time_series_with_rule(historical_data, technical_indicators)
            
    @staticmethod
    async def _analyze_time_series_with_llm(
        symbol: str,
        stock_info: Dict[str, Any],
        historical_data: pd.DataFrame,
        technical_indicators: Dict[str, float]
    ) -> Dict[str, Any]:
        """使用大语言模型分析分时数据"""
        try:
            # 获取OpenAI服务实例
            openai_service = AIService.get_openai_service()
            
            # 确保数据按日期排序
            historical_data = historical_data.sort_values('date')
            
            # 转换 DataFrame 为字典列表
            historical_data_dict = historical_data.to_dict('records')
            
            # 调用 OpenAI 服务分析时间序列
            analysis_result = await openai_service.analyze_stock_time_series(
                symbol,
                stock_info,
                historical_data_dict,
                technical_indicators
            )
            
            # 添加技术指标
            if 'indicators' not in analysis_result:
                analysis_result['indicators'] = {k: round(float(v), 2) for k, v in technical_indicators.items()}
            
            return analysis_result
                
        except Exception as e:
            print(f"Error in LLM time series analysis: {str(e)}")
            # 如果LLM分析失败，回退到规则分析
            return await AIService._analyze_time_series_with_rule(historical_data, technical_indicators) 