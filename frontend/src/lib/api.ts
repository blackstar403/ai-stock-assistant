import axios from 'axios';
import { StockInfo, StockPriceHistory, AIAnalysis, ApiResponse, CacheStats, TaskInfo, TaskCreate, TaskUpdate } from '../types';
import { indexedDBCache } from './indexedDBCache';

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

// 初始化IndexedDB缓存
if (typeof window !== 'undefined') {
  indexedDBCache.init().catch(err => {
    console.error('Failed to initialize IndexedDB cache:', err);
  });
}

// 搜索股票
export async function searchStocks(query: string, forceRefresh: boolean = false): Promise<ApiResponse<StockInfo[]>> {
  const cacheKey = `searchStocks:${query}`;
  
  // 如果不是强制刷新，尝试从缓存获取
  if (!forceRefresh) {
    const cachedResult = await indexedDBCache.get<ApiResponse<StockInfo[]>>(cacheKey);
    if (cachedResult) {
      return cachedResult;
    }
  }
  
  try {
    const response = await api.get<{success: boolean, data?: StockInfo[], error?: string}>(`/stocks/search?q=${encodeURIComponent(query)}`);
    
    // 直接返回后端的响应格式
    if (response.data) {
      // 缓存结果（1小时）
      await indexedDBCache.set(cacheKey, response.data, 3600 * 1000);
      return response.data;
    }
    
    // 如果响应不符合预期格式，进行转换
    const result = {
      success: true,
      data: response.data as any
    };
    
    // 缓存结果（1小时）
    await indexedDBCache.set(cacheKey, result, 3600 * 1000);
    
    return result;
  } catch (error) {
    console.error('Error searching stocks:', error);
    return {
      success: false,
      error: '搜索股票时出错',
    };
  }
}

// 获取股票详细信息
export async function getStockInfo(symbol: string, forceRefresh: boolean = false): Promise<ApiResponse<StockInfo>> {
  const cacheKey = `getStockInfo:${symbol}`;
  
  // 如果不是强制刷新，尝试从缓存获取
  if (!forceRefresh) {
    const cachedResult = await indexedDBCache.get<ApiResponse<StockInfo>>(cacheKey);
    if (cachedResult) {
      return cachedResult;
    }
  }
  
  try {
    const response = await api.get<{success: boolean, data?: StockInfo, error?: string}>(`/stocks/${encodeURIComponent(symbol)}`);
    
    // 直接返回后端的响应格式
    if (response.data && 'success' in response.data) {
      // 缓存结果（1小时）
      await indexedDBCache.set(cacheKey, response.data, 3600 * 1000);
      return response.data;
    }
    
    // 如果响应不符合预期格式，进行转换
    const result = {
      success: true,
      data: response.data as any
    };
    
    // 缓存结果（1小时）
    await indexedDBCache.set(cacheKey, result, 3600 * 1000);
    
    return result;
  } catch (error) {
    console.error('Error getting stock info:', error);
    return {
      success: false,
      error: '获取股票信息时出错',
    };
  }
}

// 获取股票历史价格数据
export async function getStockPriceHistory(
  symbol: string,
  interval: 'daily' | 'weekly' | 'monthly' = 'daily',
  range: '1m' | '3m' | '6m' | '1y' | '5y' = '1m',
  forceRefresh: boolean = false
): Promise<ApiResponse<StockPriceHistory>> {
  const cacheKey = `getStockPriceHistory:${symbol}:${interval}:${range}`;
  
  // 如果不是强制刷新，尝试从缓存获取
  if (!forceRefresh) {
    const cachedResult = await indexedDBCache.get<ApiResponse<StockPriceHistory>>(cacheKey);
    if (cachedResult) {
      return cachedResult;
    }
  }
  
  try {
    const response = await api.get<{success: boolean, data?: StockPriceHistory, error?: string}>(
      `/stocks/${encodeURIComponent(symbol)}/history?interval=${interval}&range=${range}`
    );
    
    // 直接返回后端的响应格式
    if (response.data && 'success' in response.data) {
      // 缓存结果（1小时）
      await indexedDBCache.set(cacheKey, response.data, 3600 * 1000);
      return response.data;
    }
    
    // 如果响应不符合预期格式，进行转换
    const result = {
      success: true,
      data: response.data as any
    };
    
    // 缓存结果（1小时）
    await indexedDBCache.set(cacheKey, result, 3600 * 1000);
    
    return result;
  } catch (error) {
    console.error('Error getting stock price history:', error);
    return {
      success: false,
      error: '获取股票价格历史数据时出错',
    };
  }
}

// 获取AI分析
export async function getAIAnalysis(
  symbol: string, 
  forceRefresh: boolean = false,
  analysisType: 'rule' | 'ml' | 'llm' = 'llm'
): Promise<ApiResponse<AIAnalysis>> {
  const cacheKey = `getAIAnalysis:${symbol}:${analysisType}`;
  
  // 如果不是强制刷新，尝试从缓存获取
  if (!forceRefresh) {
    const cachedResult = await indexedDBCache.get<ApiResponse<AIAnalysis>>(cacheKey);
    if (cachedResult) {
      return cachedResult;
    }
  }
  
  try {
    const response = await api.get<{success: boolean, data?: AIAnalysis, error?: string}>(
      `/ai/analyze?symbol=${encodeURIComponent(symbol)}&analysis_type=${analysisType}`
    );
    
    // 直接返回后端的响应格式
    if (response.data && 'success' in response.data) {
      // 缓存结果（1小时）
      await indexedDBCache.set(cacheKey, response.data, 3600 * 1000);
      return response.data;
    }
    
    // 如果响应不符合预期格式，进行转换
    const result = {
      success: true,
      data: response.data as any
    };
    
    // 缓存结果（1小时）
    await indexedDBCache.set(cacheKey, result, 3600 * 1000);
    
    return result;
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
    const response = await api.post<{success: boolean, error?: string}>('/user/saved-stocks', { symbol, notes });
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
    const response = await api.get<{success: boolean, data?: StockInfo[], error?: string}>('/user/saved-stocks');
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
    const response = await api.delete<{success: boolean, error?: string}>(`/user/saved-stocks/${symbol}`);
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
    const response = await api.post<{success: boolean, data?: { token: string }, error?: string}>('/auth/login', { email, password });
    
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
    const response = await api.post<{success: boolean, data?: { token: string }, error?: string}>('/auth/register', { name, email, password });
    
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

// 更新特定股票数据
export async function updateStockData(symbol: string): Promise<ApiResponse<any>> {
  try {
    const response = await api.post<{success: boolean, data?: {message: string}, error?: string}>(`/stocks/${symbol}/update`);
    return response.data;
  } catch (error) {
    console.error('Error updating stock data:', error);
    return {
      success: false,
      error: '更新股票数据时出错',
    };
  }
}

// 更新所有股票数据
export async function updateAllStocks(): Promise<ApiResponse<any>> {
  try {
    const response = await api.post<{success: boolean, data?: {message: string}, error?: string}>('/stocks/update-all');
    return response.data;
  } catch (error) {
    console.error('Error updating all stocks:', error);
    return {
      success: false,
      error: '更新所有股票数据时出错',
    };
  }
}

// 获取缓存统计信息
export async function getCacheStats(): Promise<ApiResponse<CacheStats>> {
  try {
    const stats = await indexedDBCache.getStats();
    return {
      success: true,
      data: {
        total_items: stats.totalItems,
        active_items: stats.activeItems,
        expired_items: stats.expiredItems,
        cache_keys: stats.cacheKeys
      }
    };
  } catch (error) {
    console.error('Error getting cache stats:', error);
    return {
      success: false,
      error: '获取缓存统计信息时出错',
    };
  }
}

// 清空缓存
export async function clearCache(): Promise<ApiResponse<any>> {
  try {
    await indexedDBCache.clear();
    return {
      success: true,
      data: { message: '缓存已清空' }
    };
  } catch (error) {
    console.error('Error clearing cache:', error);
    return {
      success: false,
      error: '清空缓存时出错',
    };
  }
}

// 清除匹配模式的缓存
export async function clearCachePattern(pattern: string): Promise<ApiResponse<any>> {
  try {
    const count = await indexedDBCache.clearPattern(pattern);
    return {
      success: true,
      data: { message: `已清除 ${count} 个缓存项` }
    };
  } catch (error) {
    console.error('Error clearing cache pattern:', error);
    return {
      success: false,
      error: '清除缓存模式时出错',
    };
  }
}

// 清理过期缓存
export async function cleanupCache(): Promise<ApiResponse<any>> {
  try {
    const count = await indexedDBCache.cleanup();
    return {
      success: true,
      data: { message: `已清理 ${count} 个过期缓存项` }
    };
  } catch (error) {
    console.error('Error cleaning up cache:', error);
    return {
      success: false,
      error: '清理过期缓存时出错',
    };
  }
}

// 获取所有定时任务
export async function getAllTasks(): Promise<ApiResponse<TaskInfo[]>> {
  try {
    const response = await api.get<{success: boolean, data?: TaskInfo[], error?: string}>('/tasks');
    return response.data;
  } catch (error) {
    console.error('Error getting all tasks:', error);
    return {
      success: false,
      error: '获取所有定时任务时出错',
    };
  }
}

// 获取特定定时任务
export async function getTask(taskId: string): Promise<ApiResponse<TaskInfo>> {
  try {
    const response = await api.get<{success: boolean, data?: TaskInfo, error?: string}>(`/tasks/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting task:', error);
    return {
      success: false,
      error: '获取定时任务时出错',
    };
  }
}

// 创建定时任务
export async function createTask(task: TaskCreate): Promise<ApiResponse<TaskInfo>> {
  try {
    const response = await api.post<{success: boolean, data?: TaskInfo, error?: string}>('/tasks', task);
    return response.data;
  } catch (error) {
    console.error('Error creating task:', error);
    return {
      success: false,
      error: '创建定时任务时出错',
    };
  }
}

// 更新定时任务
export async function updateTask(taskId: string, task: TaskUpdate): Promise<ApiResponse<TaskInfo>> {
  try {
    const response = await api.put<{success: boolean, data?: TaskInfo, error?: string}>(`/tasks/${taskId}`, task);
    return response.data;
  } catch (error) {
    console.error('Error updating task:', error);
    return {
      success: false,
      error: '更新定时任务时出错',
    };
  }
}

// 删除定时任务
export async function deleteTask(taskId: string): Promise<ApiResponse<any>> {
  try {
    const response = await api.delete<{success: boolean, data?: {message: string}, error?: string}>(`/tasks/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting task:', error);
    return {
      success: false,
      error: '删除定时任务时出错',
    };
  }
}

// 立即运行定时任务
export async function runTaskNow(taskId: string): Promise<ApiResponse<any>> {
  try {
    const response = await api.post<{success: boolean, data?: {message: string}, error?: string}>(`/tasks/${taskId}/run`);
    return response.data;
  } catch (error) {
    console.error('Error running task:', error);
    return {
      success: false,
      error: '运行定时任务时出错',
    };
  }
} 