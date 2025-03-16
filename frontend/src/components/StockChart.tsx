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
  Bar,
  BarChart,
  ComposedChart,
  ReferenceLine,
} from 'recharts';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { getStockPriceHistory, getAITimeSeriesAnalysis } from '../lib/api';
import { StockPriceHistory } from '../types';
import { RefreshCw, TrendingUp, BarChart2, Activity, AlertCircle, Brain } from 'lucide-react';
import { Skeleton } from './ui/skeleton';
import { Badge } from './ui/badge';

interface StockChartProps {
  symbol: string;
}

type TimeRange = '1m' | '3m' | '6m' | '1y' | '5y';
type Interval = 'daily' | 'weekly' | 'monthly';
type ChartType = 'price-volume';
type AnalysisType = 'rule' | 'ml' | 'llm';

// 图表数据类型
interface ChartDataPoint {
  date: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  predicted?: number;
}

export default function StockChart({ symbol }: StockChartProps) {
  const [priceHistory, setPriceHistory] = useState<StockPriceHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('1m');
  const [interval, setInterval] = useState<Interval>('daily');
  const [chartType, setChartType] = useState<ChartType>('price-volume');
  const [showAIPrediction, setShowAIPrediction] = useState(false);
  const [aiPrediction, setAIPrediction] = useState<any>(null);
  const [aiLoading, setAILoading] = useState(false);
  const [aiError, setAIError] = useState<string | null>(null);
  const [analysisType, setAnalysisType] = useState<AnalysisType>('llm');

  // 加载股票历史价格数据
  const loadPriceHistory = useCallback(async (forceRefresh: boolean = false) => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await getStockPriceHistory(symbol, interval, timeRange, forceRefresh);
      if (response.success && response.data) {
        setPriceHistory(response.data);
      } else {
        setError(response.error || '加载价格历史数据失败');
      }
    } catch (err) {
      console.error('加载价格历史数据出错:', err);
      setError('加载价格历史数据时出错');
    } finally {
      setLoading(false);
    }
  }, [symbol, interval, timeRange]);

  // 加载 AI 预测数据
  const loadAIPrediction = useCallback(async (forceRefresh: boolean = false) => {
    if (!symbol) return;
    
    setAILoading(true);
    setAIError(null);
    
    try {
      const response = await getAITimeSeriesAnalysis(
        symbol, 
        interval, 
        timeRange, 
        forceRefresh,
        analysisType
      );
      
      if (response.success && response.data) {
        setAIPrediction(response.data);
      } else {
        setAIError(response.error || '加载 AI 预测数据失败');
      }
    } catch (err) {
      console.error('加载 AI 预测数据出错:', err);
      setAIError('加载 AI 预测数据时出错');
    } finally {
      setAILoading(false);
    }
  }, [symbol, interval, timeRange, analysisType]);

  // 初始加载和参数变化时重新加载
  useEffect(() => {
    loadPriceHistory();
  }, [loadPriceHistory]);

  // 当显示 AI 预测时加载数据
  useEffect(() => {
    if (showAIPrediction) {
      loadAIPrediction();
    }
  }, [showAIPrediction, loadAIPrediction]);

  // 处理刷新
  const handleRefresh = () => {
    loadPriceHistory(true);
    if (showAIPrediction) {
      loadAIPrediction(true);
    }
  };

  // 处理切换 AI 预测
  const handleToggleAIPrediction = () => {
    setShowAIPrediction(!showAIPrediction);
  };

  // 处理切换分析类型
  const handleChangeAnalysisType = (type: AnalysisType) => {
    setAnalysisType(type);
    if (showAIPrediction) {
      loadAIPrediction(true);
    }
  };

  // 准备图表数据
  const prepareChartData = () => {
    if (!priceHistory || !priceHistory.data || priceHistory.data.length === 0) {
      return [] as ChartDataPoint[];
    }

    // 基础数据
    const chartData: ChartDataPoint[] = priceHistory.data.map(point => ({
      date: new Date(point.date).toLocaleDateString(),
      open: point.open,
      high: point.high,
      low: point.low,
      close: point.close,
      volume: point.volume,
    }));

    // 如果显示 AI 预测，添加预测数据
    if (showAIPrediction && aiPrediction && aiPrediction.prediction && aiPrediction.prediction.price_trend) {
      // 获取最后一个日期的索引
      const lastIndex = chartData.length - 1;
      const lastDate = new Date(priceHistory.data[lastIndex].date);
      
      // 添加预测数据
      aiPrediction.prediction.price_trend.forEach((point: any, index: number) => {
        // 计算预测日期（假设是工作日）
        const predictionDate = new Date(lastDate);
        predictionDate.setDate(predictionDate.getDate() + (index + 1));
        
        // 添加到图表数据
        chartData.push({
          date: predictionDate.toLocaleDateString(),
          predicted: point.predicted_price,
        });
      });
    }

    return chartData;
  };

  // 获取支撑位和阻力位
  const getSupportAndResistanceLevels = () => {
    if (!showAIPrediction || !aiPrediction || !aiPrediction.prediction) {
      return { supportLevels: [], resistanceLevels: [] };
    }
    
    return {
      supportLevels: aiPrediction.prediction.support_levels || [],
      resistanceLevels: aiPrediction.prediction.resistance_levels || [],
    };
  };

  // 获取图表颜色
  const getChartColors = () => {
    const isDarkMode = document.documentElement.classList.contains('dark');
    
    return {
      price: isDarkMode ? '#4ade80' : '#22c55e',
      volume: isDarkMode ? '#94a3b8' : '#cbd5e1',
      grid: isDarkMode ? '#334155' : '#e2e8f0',
      prediction: '#3b82f6',
      support: '#4ade80',
      resistance: '#f87171',
    };
  };

  // 渲染价格-成交量图表
  const renderPriceVolumeChart = () => {
    if (!priceHistory || !priceHistory.data || priceHistory.data.length === 0) {
      return null;
    }

    const chartData = prepareChartData();
    const colors = getChartColors();
    const { supportLevels, resistanceLevels } = getSupportAndResistanceLevels();

    return (
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" domain={['auto', 'auto']} />
            <YAxis yAxisId="right" orientation="right" domain={['auto', 'auto']} />
            <YAxis yAxisId="volume" orientation="right" domain={['auto', 'auto']} hide />
            <RechartsTooltip />
            <Legend />
            
            {/* 价格线 */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="close"
              stroke={colors.price}
              name="收盘价"
              dot={false}
              strokeWidth={2}
            />
            
            {/* 成交量柱状图 */}
            <Bar
              yAxisId="volume"
              dataKey="volume"
              fill={colors.volume}
              name="成交量"
              opacity={0.5}
            />
            
            {/* AI 预测线 */}
            {showAIPrediction && (
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="predicted"
                stroke={colors.prediction}
                name="AI预测"
                strokeDasharray="5 5"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            )}
            
            {/* 支撑位 */}
            {showAIPrediction && supportLevels.map((level: number, index: number) => (
              <ReferenceLine
                key={`support-${index}`}
                y={level}
                yAxisId="left"
                stroke={colors.support}
                strokeDasharray="3 3"
                label={{
                  value: `支撑: ${level.toFixed(2)}`,
                  position: 'insideBottomRight',
                  fill: colors.support,
                }}
              />
            ))}
            
            {/* 阻力位 */}
            {showAIPrediction && resistanceLevels.map((level: number, index: number) => (
              <ReferenceLine
                key={`resistance-${index}`}
                y={level}
                yAxisId="left"
                stroke={colors.resistance}
                strokeDasharray="3 3"
                label={{
                  value: `阻力: ${level.toFixed(2)}`,
                  position: 'insideTopRight',
                  fill: colors.resistance,
                }}
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    );
  };

  // 渲染 AI 分析结果
  const renderAIAnalysis = () => {
    if (!showAIPrediction || !aiPrediction || !aiPrediction.analysis) {
      return null;
    }
    
    const analysis = aiPrediction.analysis;
    const trend = analysis.trend;
    const strength = analysis.strength;
    
    return (
      <div className="mt-4 p-3 bg-muted rounded-md">
        <div className="flex items-center gap-2 mb-2">
          <Badge variant={trend === 'bullish' ? 'success' : trend === 'bearish' ? 'destructive' : 'secondary'}>
            {trend === 'bullish' ? '看涨' : trend === 'bearish' ? '看跌' : '中性'}
          </Badge>
          
          <Badge variant="outline">
            强度: {strength === 'strong' ? '强' : strength === 'weak' ? '弱' : '中等'}
          </Badge>
          
          <Badge variant="outline">
            分析模式: {analysisType === 'rule' ? '规则' : analysisType === 'ml' ? '机器学习' : 'LLM'}
          </Badge>
        </div>
        
        <p className="text-sm">{analysis.summary}</p>
      </div>
    );
  };

  // 渲染图表控制按钮
  const renderChartControls = () => {
    return (
      <div className="flex flex-wrap gap-2 mb-4">
        <div className="flex rounded-md overflow-hidden border border-border">
          <Button
            variant={timeRange === '1m' ? 'primary' : 'ghost'}
            size="sm"
            className="rounded-none border-0"
            onClick={() => setTimeRange('1m')}
          >
            1月
          </Button>
          <Button
            variant={timeRange === '3m' ? 'primary' : 'ghost'}
            size="sm"
            className="rounded-none border-0"
            onClick={() => setTimeRange('3m')}
          >
            3月
          </Button>
          <Button
            variant={timeRange === '6m' ? 'primary' : 'ghost'}
            size="sm"
            className="rounded-none border-0"
            onClick={() => setTimeRange('6m')}
          >
            6月
          </Button>
          <Button
            variant={timeRange === '1y' ? 'primary' : 'ghost'}
            size="sm"
            className="rounded-none border-0"
            onClick={() => setTimeRange('1y')}
          >
            1年
          </Button>
          <Button
            variant={timeRange === '5y' ? 'primary' : 'ghost'}
            size="sm"
            className="rounded-none border-0"
            onClick={() => setTimeRange('5y')}
          >
            5年
          </Button>
        </div>
        
        <div className="flex rounded-md overflow-hidden border border-border">
          <Button
            variant={interval === 'daily' ? 'primary' : 'ghost'}
            size="sm"
            className="rounded-none border-0"
            onClick={() => setInterval('daily')}
          >
            日K
          </Button>
          <Button
            variant={interval === 'weekly' ? 'primary' : 'ghost'}
            size="sm"
            className="rounded-none border-0"
            onClick={() => setInterval('weekly')}
          >
            周K
          </Button>
          <Button
            variant={interval === 'monthly' ? 'primary' : 'ghost'}
            size="sm"
            className="rounded-none border-0"
            onClick={() => setInterval('monthly')}
          >
            月K
          </Button>
        </div>
        
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={loading}
        >
          <RefreshCw className="h-4 w-4 mr-1" />
          刷新
        </Button>
        
        <Button
          variant={showAIPrediction ? 'primary' : 'outline'}
          size="sm"
          onClick={handleToggleAIPrediction}
          disabled={loading}
        >
          <Brain className="h-4 w-4 mr-1" />
          AI预测
        </Button>
      </div>
    );
  };

  // 渲染 AI 分析类型选择
  const renderAITypeControls = () => {
    if (!showAIPrediction) {
      return null;
    }
    
    return (
      <div className="flex gap-2 mt-2">
        <Button
          variant={analysisType === 'rule' ? 'primary' : 'outline'}
          size="sm"
          onClick={() => handleChangeAnalysisType('rule')}
          disabled={aiLoading}
        >
          规则分析
        </Button>
        <Button
          variant={analysisType === 'ml' ? 'primary' : 'outline'}
          size="sm"
          onClick={() => handleChangeAnalysisType('ml')}
          disabled={aiLoading}
        >
          ML分析
        </Button>
        <Button
          variant={analysisType === 'llm' ? 'primary' : 'outline'}
          size="sm"
          onClick={() => handleChangeAnalysisType('llm')}
          disabled={aiLoading}
        >
          LLM分析
        </Button>
      </div>
    );
  };

  return (
    <Card>
      <CardContent className="p-4">
        {renderChartControls()}
        
        {loading ? (
          <Skeleton className="h-80 w-full" />
        ) : error ? (
          <div className="h-80 w-full flex items-center justify-center">
            <div className="text-center">
              <AlertCircle className="h-10 w-10 text-red-500 mx-auto mb-2" />
              <p className="text-red-500">{error}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                className="mt-2"
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                重试
              </Button>
            </div>
          </div>
        ) : (
          renderPriceVolumeChart()
        )}
        
        {renderAITypeControls()}
        
        {showAIPrediction && aiLoading && (
          <Skeleton className="h-20 w-full mt-4" />
        )}
        
        {showAIPrediction && aiError && (
          <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-md">
            <p className="text-sm flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              {aiError}
            </p>
          </div>
        )}
        
        {renderAIAnalysis()}
      </CardContent>
    </Card>
  );
} 