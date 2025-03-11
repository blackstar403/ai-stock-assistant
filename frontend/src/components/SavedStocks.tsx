import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { getSavedStocks, deleteSavedStock } from '../lib/api';
import { SavedStock, StockInfo } from '../types';
import { Bookmark, Trash2, RefreshCw } from 'lucide-react';

interface SavedStocksProps {
  onSelectStock: (symbol: string) => void;
}

export default function SavedStocks({ onSelectStock }: SavedStocksProps) {
  const [savedStocks, setSavedStocks] = useState<SavedStock[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载保存的股票
  const loadSavedStocks = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getSavedStocks();
      if (response.success && response.data) {
        // 将StockInfo[]转换为SavedStock[]
        const stocks: SavedStock[] = response.data.map(stock => ({
          symbol: stock.symbol,
          name: stock.name,
          addedAt: new Date().toISOString(), // 由于API返回的是StockInfo，没有addedAt字段，这里使用当前时间
          notes: ''
        }));
        setSavedStocks(stocks);
      } else {
        setError(response.error || '加载收藏股票失败');
      }
    } catch (err) {
      console.error('加载收藏股票出错:', err);
      setError('加载收藏股票时出错');
    } finally {
      setLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    loadSavedStocks();
  }, []);

  // 删除保存的股票
  const handleDelete = async (symbol: string) => {
    try {
      const response = await deleteSavedStock(symbol);
      if (response.success) {
        // 更新本地状态
        setSavedStocks(savedStocks.filter((stock) => stock.symbol !== symbol));
      } else {
        setError(response.error || '删除股票失败');
      }
    } catch (err) {
      console.error('删除股票出错:', err);
      setError('删除股票时出错');
    }
  };

  // 格式化日期
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-xl flex items-center">
          <Bookmark className="mr-2 h-5 w-5" />
          收藏的股票
        </CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={loadSavedStocks}
          disabled={loading}
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </Button>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="py-2 text-red-500 text-center text-sm">{error}</div>
        )}
        
        {savedStocks.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">
            {loading ? '加载中...' : '暂无收藏的股票'}
          </div>
        ) : (
          <ul className="divide-y divide-border">
            {savedStocks.map((stock) => (
              <li key={stock.symbol} className="py-3">
                <div className="flex justify-between items-center">
                  <div
                    className="flex-1 cursor-pointer"
                    onClick={() => onSelectStock(stock.symbol)}
                  >
                    <div className="flex items-center">
                      <span className="font-medium">{stock.symbol}</span>
                      <span className="ml-2 text-muted-foreground">
                        {stock.name}
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      添加于: {formatDate(stock.addedAt)}
                    </div>
                    {stock.notes && (
                      <div className="text-sm mt-1 text-muted-foreground">
                        {stock.notes}
                      </div>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(stock.symbol)}
                    className="text-red-500 hover:text-red-700 hover:bg-red-100"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}