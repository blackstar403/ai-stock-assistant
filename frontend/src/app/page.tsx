'use client';

import React, { useState } from 'react';
import StockSearch from '../components/StockSearch';
import StockDetail from '../components/StockDetail';
import StockChart from '../components/StockChart';
import AIAnalysis from '../components/AIAnalysis';
import SavedStocks from '../components/SavedStocks';
import CacheControl from '../components/CacheControl';
import { StockInfo } from '../types';
import { ChartLine, Search, Settings } from 'lucide-react';
import { Button } from '../components/ui/button';
import Link from 'next/link';

export default function Home() {
  const [selectedStock, setSelectedStock] = useState<StockInfo | null>(null);

  // 处理选择股票
  const handleSelectStock = (stock: StockInfo) => {
    setSelectedStock(stock);
    
    const detailsElement = document.getElementById('stock-details-section');
    if (detailsElement) {
      detailsElement.scrollIntoView({ behavior: 'smooth' });
    }
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
            <span>AlphaBot</span>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <Link
              href="/system"
              className="flex items-center text-muted-foreground hover:text-foreground"
            >
              <Settings className="h-5 w-5 mr-1" />
              <span>系统管理</span>
            </Link>
            <a
              href="https://www.jianshu.com/c/38a7568e2b6b"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground"
            >
              简书
            </a>
            <a
              href="https://x-pai.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground"
            >
              X-PAI
            </a>
            <a
              href="https://github.com/x-pai/ai-stock-assistant"
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
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">探索股票市场</h1>
              <p className="text-muted-foreground">
                搜索股票，查看实时数据，获取AI分析和建议
              </p>
            </div>
            <div>
              <CacheControl />
            </div>
          </div>
          <StockSearch onSelectStock={handleSelectStock} />
        </div>

        {selectedStock ? (
          <div id="stock-details-section" className="grid grid-cols-1 lg:grid-cols-3 gap-8 scroll-mt-8">
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
                <h2 className="text-xl font-medium mb-2">搜索股票</h2>
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
            <p>AlphaBot &copy; {new Date().getFullYear()}</p>
            <p className="mt-2">
              免责声明：本应用提供的数据和分析仅供参考，不构成投资建议。投资决策请结合个人风险承受能力和专业意见。
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
