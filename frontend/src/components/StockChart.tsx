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
} from 'recharts';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { getStockPriceHistory } from '../lib/api';
import { StockPriceHistory } from '../types';
import { RefreshCw, TrendingUp, BarChart2, Activity, AlertCircle } from 'lucide-react';
import { Skeleton } from './ui/skeleton';
import { Badge } from './ui/badge';

interface StockChartProps {
  symbol: string;
}

type TimeRange = '1m' | '3m' | '6m' | '1y' | '5y';
type Interval = 'daily' | 'weekly' | 'monthly';
type ChartType = 'price-volume';

export default function StockChart({ symbol }: StockChartProps) {
  const [priceHistory, setPriceHistory] = useState<StockPriceHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('1m');
  const [interval, setInterval] = useState<Interval>('daily');
  const [chartType, setChartType] = useState<ChartType>('price-volume');

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
        setError(response.error || '加载数据失败');
        setPriceHistory(null);
      }
    } catch (err) {
      console.error('加载股票历史价格出错:', err);
      setError('加载数据时出错');
      setPriceHistory(null);
    } finally {
      setLoading(false);
    }
  }, [symbol, interval, timeRange]);

  // 当股票代码、时间范围或间隔变化时，加载数据
  useEffect(() => {
    loadPriceHistory();
  }, [loadPriceHistory]);

  // 检测当前主题是否为暗色模式
  const isDarkMode = () => {
    if (typeof window !== 'undefined') {
      return document.documentElement.getAttribute('data-theme') === 'dark' || 
             (window.matchMedia('(prefers-color-scheme: dark)').matches && 
              !document.documentElement.hasAttribute('data-theme'));
    }
    return false;
  };

  // 获取图表颜色
  const getChartColors = () => {
    if (!priceHistory || priceHistory.data.length === 0) {
      return {
        line: 'var(--primary)',
        volumeUp: isDarkMode() ? 'rgba(74, 222, 128, 0.7)' : 'rgba(16, 185, 129, 0.7)',
        volumeDown: isDarkMode() ? 'rgba(248, 113, 113, 0.7)' : 'rgba(239, 68, 68, 0.7)',
        grid: isDarkMode() ? 'rgba(255, 255, 255, 0.1)' : 'var(--border)',
        text: isDarkMode() ? 'rgba(255, 255, 255, 0.7)' : 'var(--muted-foreground)'
      };
    }
    
    const firstPrice = priceHistory.data[0].close;
    const lastPrice = priceHistory.data[priceHistory.data.length - 1].close;
    const isPositive = lastPrice >= firstPrice;
    
    return {
      line: isPositive 
        ? (isDarkMode() ? 'rgba(74, 222, 128, 1)' : 'var(--green-500, #10b981)') 
        : (isDarkMode() ? 'rgba(248, 113, 113, 1)' : 'var(--red-500, #ef4444)'),
      volumeUp: isDarkMode() ? 'rgba(74, 222, 128, 0.7)' : 'rgba(16, 185, 129, 0.7)',
      volumeDown: isDarkMode() ? 'rgba(248, 113, 113, 0.7)' : 'rgba(239, 68, 68, 0.7)',
      grid: isDarkMode() ? 'rgba(255, 255, 255, 0.1)' : 'var(--border)',
      text: isDarkMode() ? 'rgba(255, 255, 255, 0.7)' : 'var(--muted-foreground)'
    };
  };

  // 自定义工具提示内容
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const date = new Date(data.date);
      const formattedDate = date.toLocaleDateString();
      
      // 计算涨跌幅
      const changePercent = ((data.close - data.open) / data.open * 100).toFixed(2);
      const isPositive = data.close >= data.open;
      
      // 格式化成交量显示
      const formatVolume = (volume: number) => {
        if (volume >= 1000000000) {
          return (volume / 1000000000).toFixed(2) + 'B';
        } else if (volume >= 1000000) {
          return (volume / 1000000).toFixed(2) + 'M';
        } else if (volume >= 1000) {
          return (volume / 1000).toFixed(2) + 'K';
        }
        return volume.toString();
      };
      
      return (
        <div className="bg-card p-3 border border-border rounded-md shadow-md text-xs">
          <div className="font-medium border-b border-border pb-1 mb-1">{formattedDate}</div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-1">
            <div>
              <span className="text-muted-foreground">开盘: </span>
              <span className="font-medium">{data.open.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-muted-foreground">收盘: </span>
              <span className={`font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                {data.close.toFixed(2)}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">最高: </span>
              <span className="font-medium text-green-500">{data.high.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-muted-foreground">最低: </span>
              <span className="font-medium text-red-500">{data.low.toFixed(2)}</span>
            </div>
            <div className="col-span-2">
              <span className="text-muted-foreground">涨跌幅: </span>
              <span className={`font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                {isPositive ? '+' : ''}{changePercent}%
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-muted-foreground">成交量: </span>
              <span className="font-medium">{formatVolume(data.volume)}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  // 渲染图表
  const renderChart = (): React.ReactElement | null => {
    if (!priceHistory || priceHistory.data.length === 0) return null;
    
    const colors = getChartColors();
    
    // 为每个数据点添加涨跌标记
    const dataWithTrend = priceHistory.data.map((item, index, array) => {
      const prevItem = index > 0 ? array[index - 1] : null;
      const isRising = prevItem ? item.close >= prevItem.close : true;
      return {
        ...item,
        isRising,
        // 为上涨和下跌的成交量创建单独的数据字段
        volumeRising: isRising ? item.volume : 0,
        volumeFalling: !isRising ? item.volume : 0
      };
    });
    
    return (
      <ComposedChart
        data={dataWithTrend}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10, fill: colors.text }}
          tickFormatter={(value) => {
            const date = new Date(value);
            return `${date.getMonth() + 1}/${date.getDate()}`;
          }}
          stroke={colors.text}
        />
        <YAxis
          yAxisId="left"
          domain={['auto', 'auto']}
          tick={{ fontSize: 10, fill: colors.text }}
          tickFormatter={(value) => value.toFixed(0)}
          stroke={colors.text}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          domain={['auto', 'auto']}
          tick={{ fontSize: 10, fill: colors.text }}
          tickFormatter={(value) => (value / 1000000).toFixed(0) + 'M'}
          stroke={colors.text}
        />
        <RechartsTooltip content={<CustomTooltip />} />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="close"
          name="收盘价"
          stroke={colors.line}
          dot={false}
          activeDot={{ r: 4 }}
          strokeWidth={2}
        />
        {/* 上涨成交量 */}
        <Bar
          yAxisId="right"
          dataKey="volumeRising"
          name="成交量(上涨)"
          fill={colors.volumeUp}
          opacity={0.7}
          stackId="volume"
        />
        {/* 下跌成交量 */}
        <Bar
          yAxisId="right"
          dataKey="volumeFalling"
          name="成交量(下跌)"
          fill={colors.volumeDown}
          opacity={0.7}
          stackId="volume"
        />
      </ComposedChart>
    );
  };

  return (
    <Card className="w-full">
      <CardContent className="p-4">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center text-base font-medium">
            <TrendingUp className="mr-2 h-5 w-5 text-primary" />
            价格与成交量
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => loadPriceHistory(true)}
            disabled={loading}
            className="h-8 px-3"
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
            刷新
          </Button>
        </div>
        
        <div className="flex flex-wrap gap-2 mb-4">
          <div className="flex flex-wrap gap-1 ml-auto">
            {[
              { value: '1m', label: '1月' },
              { value: '3m', label: '3月' },
              { value: '6m', label: '6月' },
              { value: '1y', label: '1年' },
              { value: '5y', label: '5年' }
            ].map((item) => (
              <Button
                key={item.value}
                variant={timeRange === item.value ? 'secondary' : 'outline'}
                size="sm"
                onClick={() => setTimeRange(item.value as TimeRange)}
                className="h-8 px-2 text-xs"
              >
                {item.label}
              </Button>
            ))}
          </div>
        </div>
        
        <div className="flex mb-4">
          {[
            { value: 'daily', label: '日K' },
            { value: 'weekly', label: '周K' },
            { value: 'monthly', label: '月K' }
          ].map((item) => (
            <Button
              key={item.value}
              variant={interval === item.value ? 'secondary' : 'outline'}
              size="sm"
              onClick={() => setInterval(item.value as Interval)}
              className="h-8 px-2 text-xs mr-2"
            >
              {item.label}
            </Button>
          ))}
        </div>
        
        {loading && (
          <div className="flex flex-col space-y-3 py-4">
            <Skeleton className="h-60 w-full" />
          </div>
        )}
        
        {error && (
          <div className="flex flex-col justify-center items-center py-6">
            <AlertCircle className="h-8 w-8 text-red-500 mb-2" />
            <p className="text-red-500 text-sm font-medium">{error}</p>
            <Button 
              onClick={() => loadPriceHistory(true)}
              variant="outline"
              size="sm"
              className="mt-2"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              重试
            </Button>
          </div>
        )}
        
        {!loading && !error && priceHistory && priceHistory.data.length > 0 && (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              {renderChart() || <div>No chart data available</div>}
            </ResponsiveContainer>
          </div>
        )}
        
        {!loading && !error && (!priceHistory || priceHistory.data.length === 0) && (
          <div className="flex justify-center items-center h-60 text-muted-foreground">
            <p className="text-sm">暂无价格数据</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 