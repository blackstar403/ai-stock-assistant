import { NextRequest, NextResponse } from 'next/server';
import { AIAnalysis } from '../../../../types';

// 模拟AI分析数据
const mockAnalyses: Record<string, AIAnalysis> = {
  'AAPL': {
    summary: '苹果公司近期表现稳健，新产品线销售良好，服务业务持续增长。',
    sentiment: 'positive',
    keyPoints: [
      'iPhone销售超出市场预期',
      '服务业务收入同比增长15%',
      '在印度和东南亚市场份额增加',
      '供应链问题已基本解决',
    ],
    recommendation: '考虑长期持有，短期可能有小幅波动',
    riskLevel: 'low',
  },
  'MSFT': {
    summary: '微软云业务表现强劲，AI集成产品线获得市场认可，整体增长前景良好。',
    sentiment: 'positive',
    keyPoints: [
      'Azure云服务收入同比增长28%',
      'AI集成产品线获得企业客户青睐',
      'Office 365订阅用户持续增长',
      '游戏业务表现符合预期',
    ],
    recommendation: '建议增持，长期成长性佳',
    riskLevel: 'low',
  },
  'GOOGL': {
    summary: '谷歌广告业务面临一定压力，但云业务和AI发展迅速，整体前景稳定。',
    sentiment: 'neutral',
    keyPoints: [
      '广告收入增速放缓',
      'Google Cloud市场份额提升',
      'AI技术领先优势明显',
      'YouTube收入增长符合预期',
    ],
    recommendation: '建议持有，关注AI业务发展',
    riskLevel: 'medium',
  },
  'AMZN': {
    summary: '亚马逊电商业务增长稳定，AWS云服务保持领先，物流效率提升。',
    sentiment: 'positive',
    keyPoints: [
      '电商业务毛利率改善',
      'AWS保持市场领先地位',
      '物流网络优化降低成本',
      '广告业务成为新增长点',
    ],
    recommendation: '建议买入，长期增长潜力大',
    riskLevel: 'low',
  },
  'TSLA': {
    summary: '特斯拉面临激烈的市场竞争和利润率压力，但技术创新能力仍然领先。',
    sentiment: 'neutral',
    keyPoints: [
      '交付量增长但利润率下降',
      '中国市场竞争加剧',
      '自动驾驶技术进展良好',
      '能源业务增长迅速',
    ],
    recommendation: '谨慎持有，关注竞争格局变化',
    riskLevel: 'high',
  },
  'BABA': {
    summary: '阿里巴巴国内电商业务稳定，云业务增长，但面临监管和竞争压力。',
    sentiment: 'neutral',
    keyPoints: [
      '核心电商业务市场份额稳定',
      '云业务增长但盈利能力待提高',
      '国际业务扩张面临挑战',
      '监管环境趋于稳定',
    ],
    recommendation: '可考虑逢低买入，长期价值显现',
    riskLevel: 'medium',
  },
  '600519': {
    summary: '贵州茅台业绩稳健增长，高端白酒市场地位稳固，品牌价值持续提升。',
    sentiment: 'positive',
    keyPoints: [
      '高端白酒需求稳定',
      '渠道改革成效显著',
      '产品结构优化',
      '国际市场拓展顺利',
    ],
    recommendation: '长期持有，防御性较强',
    riskLevel: 'low',
  },
  '000858': {
    summary: '五粮液在次高端市场竞争力增强，产能扩张顺利，但面临行业增速放缓挑战。',
    sentiment: 'neutral',
    keyPoints: [
      '次高端产品市场份额提升',
      '渠道下沉策略成效显著',
      '产能扩张按计划进行',
      '行业整体增速放缓',
    ],
    recommendation: '可适量配置，关注消费趋势变化',
    riskLevel: 'medium',
  },
};

// 默认分析，用于未找到的股票
const defaultAnalysis: AIAnalysis = {
  summary: '暂无足够数据进行全面分析，建议收集更多信息后再做决策。',
  sentiment: 'neutral',
  keyPoints: [
    '数据有限，分析可靠性较低',
    '建议关注公司基本面',
    '参考行业整体趋势',
    '密切关注市场变化',
  ],
  recommendation: '建议收集更多信息后再做决策',
  riskLevel: 'medium',
};

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const symbol = searchParams.get('symbol')?.toUpperCase() || '';
  
  // 模拟网络延迟和AI处理时间
  await new Promise((resolve) => setTimeout(resolve, 1500));
  
  // 获取分析结果
  const analysis = mockAnalyses[symbol] || defaultAnalysis;
  
  return NextResponse.json({
    success: true,
    data: analysis,
  });
}