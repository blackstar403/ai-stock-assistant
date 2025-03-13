import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/card';
import { Button } from './ui/button';
import { getSavedStocks, deleteSavedStock } from '../lib/api';
import { SavedStock, StockInfo } from '../types';
import { Bookmark, Trash2, RefreshCw, Clock, AlertCircle, ChevronRight, Info } from 'lucide-react';
import { Skeleton } from './ui/skeleton';
import { Badge } from './ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';

interface SavedStocksProps {
  onSelectStock: (symbol: string) => void;
}

export default function SavedStocks({ onSelectStock }: SavedStocksProps) {
  const [savedStocks, setSavedStocks] = useState<SavedStock[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);

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
  const handleDelete = async (symbol: string, event: React.MouseEvent) => {
    event.stopPropagation(); // 阻止事件冒泡，避免触发选择股票
    
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

  // 处理选择股票
  const handleSelectStock = (symbol: string) => {
    setSelectedSymbol(symbol);
    onSelectStock(symbol);
  };

  return (
    <Card className="w-full h-full overflow-hidden transition-all duration-300 hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl flex items-center">
          <Bookmark className="mr-2 h-5 w-5" />
          收藏的股票
        </CardTitle>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={loadSavedStocks}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>刷新收藏列表</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="p-3 mb-3 bg-red-50 border border-red-200 rounded-md flex items-center text-red-600 text-sm">
            <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
            {error}
          </div>
        )}
        
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center space-x-2">
                <Skeleton className="h-10 w-full" />
              </div>
            ))}
          </div>
        ) : savedStocks.length === 0 ? (
          <div className="py-8 text-center">
            <div className="bg-slate-50 p-4 rounded-md">
              <Bookmark className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">暂无收藏的股票</p>
              <p className="text-xs text-muted-foreground mt-2">
                搜索并查看股票详情后，点击"收藏股票"按钮添加到此列表
              </p>
            </div>
          </div>
        ) : (
          <ul className="divide-y divide-border">
            {savedStocks.map((stock) => (
              <li 
                key={stock.symbol} 
                className={`py-3 px-2 rounded-md transition-colors duration-200 hover:bg-slate-50 cursor-pointer ${
                  selectedSymbol === stock.symbol ? 'bg-blue-50 border-l-2 border-blue-500 pl-2' : ''
                }`}
                onClick={() => handleSelectStock(stock.symbol)}
              >
                <div className="flex justify-between items-center">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <span className="font-medium">{stock.symbol}</span>
                      <span className="ml-2 text-muted-foreground">
                        {stock.name}
                      </span>
                      {selectedSymbol === stock.symbol && (
                        <Badge variant="success" className="ml-2">已选择</Badge>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1 flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      添加于: {formatDate(stock.addedAt)}
                    </div>
                    {stock.notes && (
                      <div className="text-sm mt-1 text-muted-foreground bg-slate-50 p-1 rounded">
                        <Info className="h-3 w-3 inline mr-1" />
                        {stock.notes}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => handleDelete(stock.symbol, e)}
                            className="text-red-500 hover:text-red-700 hover:bg-red-100 mr-1"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>从收藏中删除</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
      {savedStocks.length > 0 && (
        <CardFooter className="border-t pt-3 pb-3">
          <div className="w-full text-center text-xs text-muted-foreground">
            点击股票查看详细信息
          </div>
        </CardFooter>
      )}
    </Card>
  );
}