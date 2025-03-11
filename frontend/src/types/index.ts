// 股票基本信息
export interface StockInfo {
  symbol: string;
  name: string;
  exchange: string;
  currency: string;
  price?: number;
  change?: number;
  changePercent?: number;
  marketCap?: number;
  volume?: number;
}

// 股票历史价格数据点
export interface StockPricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 股票历史价格数据
export interface StockPriceHistory {
  symbol: string;
  data: StockPricePoint[];
}

// AI分析结果
export interface AIAnalysis {
  summary: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  keyPoints: string[];
  recommendation: string;
  riskLevel: 'low' | 'medium' | 'high';
}

// 用户保存的股票
export interface SavedStock {
  symbol: string;
  name: string;
  addedAt: string;
  notes?: string;
}

// API响应
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
} 