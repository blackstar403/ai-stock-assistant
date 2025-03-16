import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
  Area,
  AreaChart,
  ReferenceLine,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { getAITimeSeriesAnalysis } from '../lib/api';
import { Skeleton } from './ui/skeleton';
import { Badge } from './ui/badge';
import { RefreshCw, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

interface AITimeSeriesAnalysisProps {
  symbol: string;
  interval?: 'daily' | 'weekly' | 'monthly';
  range?: '1m' | '3m' | '6m' | '1y' | '5y';
}

export default function AITimeSeriesAnalysis({ 
  symbol, 
  interval = 'daily', 
  range = '1m' 
}: AITimeSeriesAnalysisProps) {
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisType, setAnalysisType] = useState<'rule' | 'ml' | 'llm'>('llm');

  // 加载AI分时分析数据
  const loadAnalysisData = useCallback(async (forceRefresh: boolean = false) => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await getAITimeSeriesAnalysis(
        symbol, 
        interval, 
        range, 
        forceRefresh, 
        analysisType
      );
      
      if (response.success && response.data) {
        setAnalysisData(response.data);
      } else {
        setError(response.error || '无法获取AI分时分析');
      }
    } catch (error) {
      setError('获取AI分时分析时出错');
      console.error('获取AI分时分析时出错:', error);
    } finally {
      setLoading(false);
    }
  }, [symbol, interval, range, analysisType]);

  // 初始加载和参数变化时重新加载
  useEffect(() => {
    loadAnalysisData();
  }, [loadAnalysisData]);

  // 判断是否为暗色模式
  const isDarkMode = () => {
    return document.documentElement.classList.contains('dark');
  };

  // 获取图表颜色
  const getChartColors = () => {
    const darkMode = isDarkMode();
    
    return {
      bullish: darkMode ? '#4ade80' : '#22c55e',
      bearish: darkMode ? '#f87171' : '#ef4444',
      neutral: darkMode ? '#94a3b8' : '#64748b',
      grid: darkMode ? '#334155' : '#e2e8f0',
      text: darkMode ? '#f8fafc' : '#0f172a',
      background: darkMode ? '#1e293b' : '#f8fafc',
    };
  };

  // 自定义工具提示
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border p-2 rounded-md shadow-md">
          <p className="text-sm font-medium">{`Day ${payload[0].payload.day}`}</p>
          <p className="text-sm">{`预测价格: ${payload[0].value.toFixed(2)}`}</p>
        </div>
      );
    }
    return null;
  };

  // 渲染预测图表
  const renderPredictionChart = () => {
    if (!analysisData || !analysisData.prediction || !analysisData.prediction.price_trend) {
      return null;
    }

    const colors = getChartColors();
    const trend = analysisData.analysis?.trend || 'neutral';
    const lineColor = trend === 'bullish' ? colors.bullish : trend === 'bearish' ? colors.bearish : colors.neutral;
    
    // 准备图表数据
    const chartData = analysisData.prediction.price_trend.map((point: any) => ({
      day: point.day,
      price: point.predicted_price
    }));

    // 支撑位和阻力位
    const supportLevels = analysisData.prediction.support_levels || [];
    const resistanceLevels = analysisData.prediction.resistance_levels || [];

    return (
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
            <XAxis 
              dataKey="day" 
              label={{ value: '天数', position: 'insideBottom', offset: -5 }} 
              stroke={colors.text}
            />
            <YAxis stroke={colors.text} />
            <RechartsTooltip content={<CustomTooltip />} />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke={lineColor} 
              strokeWidth={2}
              dot={{ r: 4, strokeWidth: 1 }}
              activeDot={{ r: 6, strokeWidth: 1 }}
            />
            
            {/* 支撑位 */}
            {supportLevels.map((level: number, index: number) => (
              <ReferenceLine 
                key={`support-${index}`} 
                y={level} 
                stroke={colors.bullish} 
                strokeDasharray="3 3" 
                label={{ 
                  value: `支撑: ${level.toFixed(2)}`, 
                  position: 'insideBottomRight',
                  fill: colors.bullish
                }} 
              />
            ))}
            
            {/* 阻力位 */}
            {resistanceLevels.map((level: number, index: number) => (
              <ReferenceLine 
                key={`resistance-${index}`} 
                y={level} 
                stroke={colors.bearish} 
                strokeDasharray="3 3" 
                label={{ 
                  value: `阻力: ${level.toFixed(2)}`, 
                  position: 'insideTopRight',
                  fill: colors.bearish
                }} 
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  // 渲染技术指标
  const renderIndicators = () => {
    if (!analysisData || !analysisData.indicators) {
      return null;
    }

    const indicators = analysisData.indicators;
    
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-4">
        {Object.entries(indicators).map(([key, value]) => (
          <div key={key} className="bg-muted p-2 rounded-md">
            <div className="text-xs text-muted-foreground">{key}</div>
            <div className="text-sm font-medium">{typeof value === 'number' ? value.toFixed(2) : String(value)}</div>
          </div>
        ))}
      </div>
    );
  };

  // 渲染分析结果
  const renderAnalysis = () => {
    if (!analysisData || !analysisData.analysis) {
      return null;
    }

    const analysis = analysisData.analysis;
    const trend = analysis.trend;
    const strength = analysis.strength;
    
    return (
      <div className="mt-4">
        <div className="flex items-center gap-2 mb-2">
          <Badge variant={trend === 'bullish' ? 'success' : trend === 'bearish' ? 'destructive' : 'secondary'}>
            {trend === 'bullish' ? (
              <TrendingUp className="h-3 w-3 mr-1" />
            ) : trend === 'bearish' ? (
              <TrendingDown className="h-3 w-3 mr-1" />
            ) : null}
            {trend === 'bullish' ? '看涨' : trend === 'bearish' ? '看跌' : '中性'}
          </Badge>
          
          <Badge variant="outline">
            强度: {strength === 'strong' ? '强' : strength === 'weak' ? '弱' : '中等'}
          </Badge>
        </div>
        
        <p className="text-sm">{analysis.summary}</p>
      </div>
    );
  };

  // 渲染加载状态
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>AI分时分析</CardTitle>
          <CardDescription>加载中...</CardDescription>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-4">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>AI分时分析</CardTitle>
          <CardDescription className="text-destructive flex items-center">
            <AlertCircle className="h-4 w-4 mr-1" />
            {error}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => loadAnalysisData(true)}>
            <RefreshCw className="h-4 w-4 mr-2" />
            重试
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>AI分时分析</CardTitle>
            <CardDescription>
              基于{interval === 'daily' ? '日' : interval === 'weekly' ? '周' : '月'}K线的AI预测分析
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => loadAnalysisData(true)}>
            <RefreshCw className="h-4 w-4 mr-2" />
            刷新
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="prediction">
          <TabsList className="mb-4">
            <TabsTrigger value="prediction">价格预测</TabsTrigger>
            <TabsTrigger value="indicators">技术指标</TabsTrigger>
          </TabsList>
          
          <TabsContent value="prediction">
            {renderPredictionChart()}
            {renderAnalysis()}
          </TabsContent>
          
          <TabsContent value="indicators">
            {renderIndicators()}
          </TabsContent>
        </Tabs>
        
        <div className="mt-4 flex justify-between">
          <div className="flex gap-2">
            <Button 
              variant={analysisType === 'rule' ? 'primary' : 'outline'} 
              size="sm"
              onClick={() => setAnalysisType('rule')}
            >
              规则分析
            </Button>
            <Button 
              variant={analysisType === 'ml' ? 'primary' : 'outline'} 
              size="sm"
              onClick={() => setAnalysisType('ml')}
            >
              ML分析
            </Button>
            <Button 
              variant={analysisType === 'llm' ? 'primary' : 'outline'} 
              size="sm"
              onClick={() => setAnalysisType('llm')}
            >
              LLM分析
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 