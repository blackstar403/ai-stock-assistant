"""
OpenAI 服务，用于与 OpenAI API 交互
"""

import openai
from typing import Dict, Any, List, Optional
import json

from app.core.config import settings

class OpenAIService:
    """OpenAI 服务类，用于与 OpenAI API 交互"""
    
    def __init__(self):
        """初始化 OpenAI 客户端"""
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )
        self.model = settings.OPENAI_MODEL
    
    async def analyze_stock(
        self, 
        symbol: str, 
        stock_info: Dict[str, Any], 
        historical_data: Dict[str, Any],
        fundamentals: Dict[str, Any],
        news_sentiment: Dict[str, Any],
        sector_linkage: Dict[str, Any],
        concept_distribution: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用 OpenAI 分析股票"""
        try:
            # 准备提示词
            prompt = self._prepare_prompt(
                symbol, 
                stock_info, 
                historical_data,
                fundamentals,
                technical_indicators,
                news_sentiment,
                sector_linkage,
                concept_distribution
            )
            
            # 调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师，擅长分析股票数据并提供投资建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return result
        except Exception as e:
            print(f"OpenAI 分析股票时出错: {str(e)}")
            return {
                "summary": f"无法生成分析: {str(e)}",
                "sentiment": "neutral",
                "keyPoints": ["分析生成失败"],
                "recommendation": "无法提供建议",
                "riskLevel": "medium"
            }
    
    def _prepare_prompt(
        self, 
        symbol: str, 
        stock_info: Dict[str, Any], 
        historical_data: Dict[str, Any],
        fundamentals: Dict[str, Any],
        technical_indicators: Dict[str, Any],
        news_sentiment: Dict[str, Any],
        sector_linkage: Dict[str, Any],
        concept_distribution: Dict[str, Any]
    ) -> str:
        """准备 OpenAI 提示词"""
        # 格式化历史数据
        historical_summary = "最近价格走势:\n"
        if historical_data and len(historical_data) > 0:
            recent_data = list(historical_data.items())[-10:]  # 最近10天数据
            for date, data in recent_data:
                historical_summary += f"- {date}: 开盘 {data['open']:.2f}, 收盘 {data['close']:.2f}, 最高 {data['high']:.2f}, 最低 {data['low']:.2f}, 成交量 {data['volume']}\n"
        
        # 格式化技术指标
        technical_summary = "技术指标:\n"
        
        # 先添加重要的布林带和200日均线指标（如果存在）
        if 'BB_Description' in technical_indicators:
            technical_summary += f"- {technical_indicators['BB_Description']}\n"
        
        if 'SMA200_Description' in technical_indicators:
            technical_summary += f"- {technical_indicators['SMA200_Description']}\n"
        
        # 添加其他技术指标
        for indicator, value in technical_indicators.items():
            # 跳过已经添加的描述性指标和非数值指标
            if indicator in ['BB_Description', 'SMA200_Description', 'ProfessionalSpeculationPrinciples'] or not isinstance(value, (int, float)):
                continue
            technical_summary += f"- {indicator}: {value:.2f}\n"
        
        # 格式化基本面数据
        fundamental_summary = "基本面数据:\n"
        important_metrics = [
            "PERatio", "PBRatio", "DividendYield", "MarketCapitalization", 
            "EPS", "ROE", "ROA", "DebtToEquity"
        ]
        for metric in important_metrics:
            if metric in fundamentals:
                fundamental_summary += f"- {metric}: {fundamentals[metric]}\n"
        
        # 格式化新闻情绪
        news_summary = "新闻情绪:\n"
        if "feed" in news_sentiment and news_sentiment["feed"]:
            for i, article in enumerate(news_sentiment["feed"][:5]):  # 最多5条新闻
                news_summary += f"- 标题: {article.get('title', 'N/A')}\n"
                news_summary += f"  情绪分数: {article.get('overall_sentiment_score', 0)}\n"
        else:
            news_summary += "- 无相关新闻\n"
        
        # 格式化政策共振信息
        policy_summary = ""
        if "policy_resonance" in news_sentiment:
            policy_resonance = news_sentiment["policy_resonance"]
            coefficient = policy_resonance.get("coefficient", 0)
            policies = policy_resonance.get("policies", [])
            
            if coefficient > 0:
                policy_summary = f"""
政策共振分析:
- 共振系数: {coefficient:.2f} (0-1之间，越高表示与政策关联度越高)
"""
                if policies:
                    policy_summary += "- 相关政策:\n"
                    for policy in policies:
                        policy_summary += f"  * {policy.get('title', 'N/A')} ({policy.get('date', 'N/A')}) - 相关度: {policy.get('relevance', 0)}\n"
        
        # 格式化板块联动性信息
        sector_summary = ""
        sector_name = sector_linkage.get('sector_name', '未知板块')
        sector_driving_force = sector_linkage.get('driving_force', 0)
        sector_correlation = sector_linkage.get('correlation', 0)
        sector_rank = sector_linkage.get('rank_in_sector', 0)
        sector_total = sector_linkage.get('total_in_sector', 0)
        
        sector_summary = f"""
板块联动性分析:
- 所属板块: {sector_name}
- 板块带动性: {sector_driving_force:.2f} (0-1之间，越高表示对板块的带动作用越强)
- 板块联动性: {sector_correlation:.2f} (0-1之间，越高表示与板块整体走势越同步)
"""
        if sector_rank > 0 and sector_total > 0:
            sector_summary += f"- 板块排名: {sector_rank}/{sector_total}\n"
        
        # 格式化概念涨跌分布信息
        concept_summary = ""
        concept_strength = concept_distribution.get('overall_strength', 0)
        leading_concepts = concept_distribution.get('leading_concepts', [])
        lagging_concepts = concept_distribution.get('lagging_concepts', [])
        all_concepts = concept_distribution.get('all_concepts', [])
        
        concept_summary = f"""
概念涨跌分布分析:
- 概念整体强度: {concept_strength:.2f} (0-1之间，越高表示所属概念整体越强势)
"""
        
        if leading_concepts:
            concept_summary += "- 表现领先的概念:\n"
            for concept in leading_concepts[:3]:  # 最多显示3个
                concept_summary += f"  * {concept.get('name', 'N/A')} - 强度: {concept.get('strength', 0):.2f}, 排名: {concept.get('rank', 0)}/{concept.get('total', 0)}\n"
        
        if lagging_concepts:
            concept_summary += "- 表现落后的概念:\n"
            for concept in lagging_concepts[:2]:  # 最多显示2个
                concept_summary += f"  * {concept.get('name', 'N/A')} - 强度: {concept.get('strength', 0):.2f}, 排名: {concept.get('rank', 0)}/{concept.get('total', 0)}\n"
        
        if all_concepts and len(all_concepts) > 0:
            concept_summary += f"- 所属概念数量: {len(all_concepts)}\n"
        
        # 添加《专业投机原理》的分析框架
        professional_principles = ""
        if 'ProfessionalSpeculationPrinciples' in technical_indicators:
            professional_principles = f"""
《专业投机原理》分析框架:
{technical_indicators['ProfessionalSpeculationPrinciples']}

根据《专业投机原理》，请特别关注:
1. 价格相对于200日均线的位置（判断长期趋势）
2. 布林带指标的位置和宽度（判断短期超买超卖和波动性）
3. 趋势跟踪策略（顺势而为，避免逆势操作）
4. 政策共振因素（政策与股票的相关性）
5. 板块联动性和个股地位（判断个股带动性和主动性）
6. 概念涨跌分布（判断概念支撑强度）
"""
        
        # 构建完整提示词
        prompt = f"""
请分析以下股票数据并提供专业的投资建议。

股票代码: {symbol}
股票名称: {stock_info.get('name', 'N/A')}
当前价格: {stock_info.get('price', 'N/A')}
涨跌幅: {stock_info.get('changePercent', 'N/A')}%

{historical_summary}

{technical_summary}

{fundamental_summary}

{news_summary}

{policy_summary}

{sector_summary}

{concept_summary}

{professional_principles}

请提供以下格式的JSON分析结果:
1. summary: 对股票当前状况的简要总结，包括价格相对于200日均线和布林带的位置，以及政策共振情况、板块地位和概念强度
2. sentiment: 市场情绪 (positive, neutral, negative)
3. keyPoints: 关键分析点列表 (至少7点)，包括对布林带、200日均线、政策共振、板块联动性和概念涨跌分布的分析
4. recommendation: 投资建议，参考《专业投机原理》的趋势跟踪策略，并考虑政策共振因素、板块地位和概念强度
5. riskLevel: 风险水平 (low, medium, high)

请确保返回的是有效的JSON格式。
"""
        
        return prompt 