'use client';

import React, { useState } from 'react';
import StockSearch from '../components/StockSearch';
import StockDetail from '../components/StockDetail';
import StockChart from '../components/StockChart';
import AIAnalysis from '../components/AIAnalysis';
import SavedStocks from '../components/SavedStocks';
import { StockInfo } from '../types';
import { ChartLine, Bot, Search } from 'lucide-react';

export default function Home() {
  const [selectedStock, setSelectedStock] = useState<StockInfo | null>(null);

  // 处理选择股票
  const handleSelectStock = (stock: StockInfo) => {
    setSelectedStock(stock);
  };

  // 处理从收藏夹选择股票
  const handleSelectFromSaved = (symbol: string) => {
    // 这里简单处理，只设置symbol
    setSelectedStock({
      symbol,
      name: '',
      exchange: '',
      currency: '',
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center">
          <div className="flex items-center text-2xl font-bold text-primary">
            <ChartLine className="h-6 w-6 mr-2" />
            <span>AI股票助理</span>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <a
              href="https://github.com/yourusername/ai-stock-assistant"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground"
            >
              GitHub
            </a>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-4">探索股票市场</h1>
          <p className="text-muted-foreground mb-6">
            搜索股票，查看实时数据，获取AI分析和建议
          </p>
          <StockSearch onSelectStock={handleSelectStock} />
        </div>

        {selectedStock ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              <StockDetail symbol={selectedStock.symbol} />
              <StockChart symbol={selectedStock.symbol} />
              <AIAnalysis symbol={selectedStock.symbol} />
            </div>
            <div>
              <SavedStocks onSelectStock={handleSelectFromSaved} />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 flex items-center justify-center p-16 border border-dashed border-border rounded-lg">
              <div className="text-center">
                <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h2 className="text-xl font-medium mb-2">搜索股票开始</h2>
                <p className="text-muted-foreground">
                  输入股票代码或名称，查看详细信息和AI分析
                </p>
              </div>
            </div>
            <div>
              <SavedStocks onSelectStock={handleSelectFromSaved} />
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-border mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-muted-foreground text-sm">
            <p>AI股票助理 &copy; {new Date().getFullYear()}</p>
            <p className="mt-2">
              免责声明：本应用提供的数据和分析仅供参考，不构成投资建议。投资决策请结合个人风险承受能力和专业意见。
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
