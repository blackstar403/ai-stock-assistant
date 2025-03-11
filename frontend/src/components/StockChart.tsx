import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Button } from './ui/button';
import { getStockPriceHistory } from '../lib/api';
import { StockPriceHistory } from '../types';

interface StockChartProps {
  symbol: string;
}

type TimeRange = '1m' | '3m' | '6m' | '1y' | '5y';
type Interval = 'daily' | 'weekly' | 'monthly';

export default function StockChart({ symbol }: StockChartProps) {
  const [priceHistory, setPriceHistory] = useState<StockPriceHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('1m');
  const [interval, setInterval] = useState<Interval>('daily');

  // 加载股票历史价格数据
  useEffect(() => {
    async function loadPriceHistory() {
      if (!symbol) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const response = await getStockPriceHistory(symbol, interval, timeRange);
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
    }
    
    loadPriceHistory();
  }, [symbol, interval, timeRange]);

  // 格式化工具提示内容
  const formatTooltip = (value: number) => {
    return value.toFixed(2);
  };

  // 自定义工具提示内容
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card p-3 border border-border rounded shadow-sm">
          <p className="font-medium">{label}</p>
          <p className="text-sm">
            <span className="text-blue-500">开盘: </span>
            {payload[0].payload.open.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="text-green-500">最高: </span>
            {payload[0].payload.high.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="text-red-500">最低: </span>
            {payload[0].payload.low.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="text-purple-500">收盘: </span>
            {payload[0].payload.close.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="text-gray-500">成交量: </span>
            {payload[0].payload.volume.toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="flex flex-wrap gap-2 mb-4">
        <div className="flex rounded-md overflow-hidden border border-border">
          <Button
            variant={timeRange === '1m' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setTimeRange('1m')}
            className="rounded-none"
          >
            1月
          </Button>
          <Button
            variant={timeRange === '3m' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setTimeRange('3m')}
            className="rounded-none"
          >
            3月
          </Button>
          <Button
            variant={timeRange === '6m' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setTimeRange('6m')}
            className="rounded-none"
          >
            6月
          </Button>
          <Button
            variant={timeRange === '1y' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setTimeRange('1y')}
            className="rounded-none"
          >
            1年
          </Button>
          <Button
            variant={timeRange === '5y' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setTimeRange('5y')}
            className="rounded-none"
          >
            5年
          </Button>
        </div>
        
        <div className="flex rounded-md overflow-hidden border border-border">
          <Button
            variant={interval === 'daily' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setInterval('daily')}
            className="rounded-none"
          >
            日
          </Button>
          <Button
            variant={interval === 'weekly' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setInterval('weekly')}
            className="rounded-none"
          >
            周
          </Button>
          <Button
            variant={interval === 'monthly' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setInterval('monthly')}
            className="rounded-none"
          >
            月
          </Button>
        </div>
      </div>
      
      {loading && (
        <div className="flex justify-center items-center h-80">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      )}
      
      {error && (
        <div className="flex justify-center items-center h-80 text-red-500">
          {error}
        </div>
      )}
      
      {!loading && !error && priceHistory && priceHistory.data.length > 0 && (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={priceHistory.data}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
                stroke="var(--muted-foreground)"
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => value.toFixed(0)}
                stroke="var(--muted-foreground)"
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="close"
                name="收盘价"
                stroke="var(--primary)"
                dot={false}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      
      {!loading && !error && (!priceHistory || priceHistory.data.length === 0) && (
        <div className="flex justify-center items-center h-80 text-muted-foreground">
          暂无价格数据
        </div>
      )}
    </div>
  );
} 