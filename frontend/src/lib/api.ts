import axios from 'axios';
import { StockInfo, StockPriceHistory, AIAnalysis, ApiResponse } from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 搜索股票
export async function searchStocks(query: string): Promise<ApiResponse<StockInfo[]>> {
  try {
    const response = await api.get<ApiResponse<StockInfo[]>>(`/stocks/search?q=${encodeURIComponent(query)}`);
    return response.data;
  } catch (error) {
    console.error('Error searching stocks:', error);
    return {
      success: false,
      error: '搜索股票时出错',
    };
  }
}

// 获取股票详情
export async function getStockInfo(symbol: string): Promise<ApiResponse<StockInfo>> {
  try {
    const response = await api.get<ApiResponse<StockInfo>>(`/stocks/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Error getting stock info:', error);
    return {
      success: false,
      error: '获取股票信息时出错',
    };
  }
}

// 获取股票历史价格
export async function getStockPriceHistory(
  symbol: string,
  interval: 'daily' | 'weekly' | 'monthly' = 'daily',
  range: '1m' | '3m' | '6m' | '1y' | '5y' = '1m'
): Promise<ApiResponse<StockPriceHistory>> {
  try {
    const response = await api.get<ApiResponse<StockPriceHistory>>(
      `/stocks/${symbol}/history?interval=${interval}&range=${range}`
    );
    return response.data;
  } catch (error) {
    console.error('Error getting stock price history:', error);
    return {
      success: false,
      error: '获取股票历史价格时出错',
    };
  }
}

// 获取AI分析
export async function getAIAnalysis(symbol: string): Promise<ApiResponse<AIAnalysis>> {
  try {
    const response = await api.get<ApiResponse<AIAnalysis>>(`/ai/analyze?symbol=${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Error getting AI analysis:', error);
    return {
      success: false,
      error: '获取AI分析时出错',
    };
  }
}

// 保存股票到收藏夹
export async function saveStock(symbol: string, notes?: string): Promise<ApiResponse<void>> {
  try {
    const response = await api.post<ApiResponse<void>>('/user/saved-stocks', { symbol, notes });
    return response.data;
  } catch (error) {
    console.error('Error saving stock:', error);
    return {
      success: false,
      error: '保存股票时出错',
    };
  }
}

// 获取已保存的股票
export async function getSavedStocks(): Promise<ApiResponse<StockInfo[]>> {
  try {
    const response = await api.get<ApiResponse<StockInfo[]>>('/user/saved-stocks');
    return response.data;
  } catch (error) {
    console.error('Error getting saved stocks:', error);
    return {
      success: false,
      error: '获取已保存股票时出错',
    };
  }
}

// 删除已保存的股票
export async function deleteSavedStock(symbol: string): Promise<ApiResponse<void>> {
  try {
    const response = await api.delete<ApiResponse<void>>(`/user/saved-stocks/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting saved stock:', error);
    return {
      success: false,
      error: '删除已保存股票时出错',
    };
  }
} 