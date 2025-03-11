import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { getStockInfo, saveStock } from '../lib/api';
import { StockInfo } from '../types';
import { Bookmark, BookmarkCheck, BarChart3 } from 'lucide-react';

interface StockDetailProps {
  symbol: string;
}

export default function StockDetail({ symbol }: StockDetailProps) {
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [notes, setNotes] = useState('');
  const [savingNotes, setSavingNotes] = useState(false);

  // 加载股票信息
  useEffect(() => {
    async function loadStockInfo() {
      if (!symbol) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const response = await getStockInfo(symbol);
        if (response.success && response.data) {
          setStockInfo(response.data);
        } else {
          setError(response.error || '加载股票信息失败');
          setStockInfo(null);
        }
      } catch (err) {
        console.error('加载股票信息出错:', err);
        setError('加载股票信息时出错');
        setStockInfo(null);
      } finally {
        setLoading(false);
      }
    }
    
    loadStockInfo();
  }, [symbol]);

  // 保存股票到收藏夹
  const handleSaveStock = async () => {
    if (!stockInfo) return;
    
    setSavingNotes(true);
    try {
      const response = await saveStock(stockInfo.symbol, notes);
      if (response.success) {
        setIsSaved(true);
      } else {
        setError(response.error || '保存股票失败');
      }
    } catch (err) {
      console.error('保存股票出错:', err);
      setError('保存股票时出错');
    } finally {
      setSavingNotes(false);
    }
  };

  // 格式化数字
  const formatNumber = (num: number | undefined, decimals = 2) => {
    if (num === undefined) return '-';
    return num.toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  // 格式化市值
  const formatMarketCap = (marketCap: number | undefined) => {
    if (marketCap === undefined) return '-';
    
    if (marketCap >= 1000000000000) {
      return `${(marketCap / 1000000000000).toFixed(2)}万亿`;
    } else if (marketCap >= 100000000) {
      return `${(marketCap / 100000000).toFixed(2)}亿`;
    } else if (marketCap >= 10000) {
      return `${(marketCap / 10000).toFixed(2)}万`;
    }
    
    return formatNumber(marketCap, 0);
  };

  return (
    <Card className="w-full">
      {loading && (
        <CardContent className="flex justify-center items-center py-16">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </CardContent>
      )}
      
      {error && (
        <CardContent className="py-8 text-red-500 text-center">{error}</CardContent>
      )}
      
      {!loading && !error && stockInfo && (
        <>
          <CardHeader className="flex flex-row items-start justify-between">
            <div>
              <div className="flex items-center">
                <CardTitle className="text-2xl">{stockInfo.symbol}</CardTitle>
                <span className="ml-2 text-muted-foreground">
                  {stockInfo.name}
                </span>
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {stockInfo.exchange} · {stockInfo.currency}
              </div>
            </div>
            <div className="text-right">
              {stockInfo.price !== undefined && (
                <div className="text-2xl font-bold">
                  {formatNumber(stockInfo.price)}
                </div>
              )}
              {stockInfo.change !== undefined && stockInfo.changePercent !== undefined && (
                <div
                  className={`text-sm font-medium ${
                    stockInfo.change > 0
                      ? 'text-green-500'
                      : stockInfo.change < 0
                      ? 'text-red-500'
                      : 'text-muted-foreground'
                  }`}
                >
                  {stockInfo.change > 0 ? '+' : ''}
                  {formatNumber(stockInfo.change)} ({stockInfo.changePercent > 0 ? '+' : ''}
                  {formatNumber(stockInfo.changePercent)}%)
                </div>
              )}
            </div>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">市值</div>
                <div className="font-medium">
                  {formatMarketCap(stockInfo.marketCap)}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">成交量</div>
                <div className="font-medium">
                  {stockInfo.volume ? formatNumber(stockInfo.volume, 0) : '-'}
                </div>
              </div>
            </div>
            
            <div className="pt-4 border-t border-border">
              <div className="flex items-center mb-2">
                <BarChart3 className="h-4 w-4 mr-2" />
                <h3 className="font-medium">添加到收藏</h3>
              </div>
              <div className="space-y-2">
                <Input
                  placeholder="添加笔记（可选）"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
                <Button
                  onClick={handleSaveStock}
                  className="w-full"
                  isLoading={savingNotes}
                  disabled={isSaved}
                >
                  {!savingNotes && (
                    <>
                      {isSaved ? (
                        <BookmarkCheck className="h-4 w-4 mr-2" />
                      ) : (
                        <Bookmark className="h-4 w-4 mr-2" />
                      )}
                    </>
                  )}
                  {isSaved ? '已收藏' : '收藏股票'}
                </Button>
              </div>
            </div>
          </CardContent>
        </>
      )}
    </Card>
  );
} 