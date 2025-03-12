import axios from 'axios';
import { StockInfo, StockPriceHistory, AIAnalysis, ApiResponse } from '../types';

// API基础URL，优先使用环境变量，否则使用相对路径
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证令牌
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取令牌
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    
    // 如果有令牌，添加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理认证错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 如果是401错误（未授权），可以重定向到登录页面
    if (error.response && error.response.status === 401) {
      // 清除本地存储的令牌
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        // 可以在这里添加重定向到登录页面的逻辑
        // window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

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

// 用户登录
export async function login(email: string, password: string): Promise<ApiResponse<{ token: string }>> {
  try {
    const response = await api.post<ApiResponse<{ token: string }>>('/auth/login', { email, password });
    
    // 如果登录成功，保存令牌到localStorage
    if (response.data.success && response.data.data?.token) {
      localStorage.setItem('auth_token', response.data.data.token);
    }
    
    return response.data;
  } catch (error) {
    console.error('Error logging in:', error);
    return {
      success: false,
      error: '登录失败，请检查您的凭据',
    };
  }
}

// 用户注册
export async function register(name: string, email: string, password: string): Promise<ApiResponse<{ token: string }>> {
  try {
    const response = await api.post<ApiResponse<{ token: string }>>('/auth/register', { name, email, password });
    
    // 如果注册成功，保存令牌到localStorage
    if (response.data.success && response.data.data?.token) {
      localStorage.setItem('auth_token', response.data.data.token);
    }
    
    return response.data;
  } catch (error) {
    console.error('Error registering:', error);
    return {
      success: false,
      error: '注册失败，请稍后再试',
    };
  }
}

// 退出登录
export function logout(): void {
  localStorage.removeItem('auth_token');
  // 可以在这里添加重定向到登录页面的逻辑
  // window.location.href = '/login';
}

// 检查用户是否已登录
export function isLoggedIn(): boolean {
  return typeof window !== 'undefined' && !!localStorage.getItem('auth_token');
} 