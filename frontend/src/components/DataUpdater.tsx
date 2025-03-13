import React, { useState } from 'react';
import { updateStockData, updateAllStocks } from '../lib/api';

const DataUpdater: React.FC = () => {
  const [symbol, setSymbol] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // 更新特定股票数据
  const handleUpdateStock = async () => {
    if (!symbol.trim()) {
      setError('请输入股票代码');
      return;
    }
    
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      const response = await updateStockData(symbol);
      if (response.success) {
        setMessage(response.data?.message || `已开始更新股票 ${symbol} 的数据`);
        setSymbol(''); // 清空输入
      } else {
        setError(response.error || '更新股票数据失败');
      }
    } catch (err) {
      setError('更新股票数据时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 更新所有股票数据
  const handleUpdateAllStocks = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      const response = await updateAllStocks();
      if (response.success) {
        setMessage(response.data?.message || '已开始更新所有股票数据');
      } else {
        setError(response.error || '更新所有股票数据失败');
      }
    } catch (err) {
      setError('更新所有股票数据时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">数据更新</h2>
      
      {/* 错误提示 */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {/* 成功消息 */}
      {message && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {message}
        </div>
      )}
      
      {/* 更新特定股票 */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">更新特定股票数据</h3>
        <div className="flex space-x-2">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="输入股票代码"
            className="flex-1 border rounded px-3 py-2"
          />
          <button
            onClick={handleUpdateStock}
            disabled={loading || !symbol.trim()}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-blue-300"
          >
            {loading ? '更新中...' : '更新'}
          </button>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          输入股票代码，例如: AAPL, MSFT, GOOG
        </p>
      </div>
      
      {/* 更新所有股票 */}
      <div>
        <h3 className="text-lg font-medium mb-2">更新所有股票数据</h3>
        <button
          onClick={handleUpdateAllStocks}
          disabled={loading}
          className="bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600 disabled:bg-indigo-300"
        >
          {loading ? '更新中...' : '更新所有股票'}
        </button>
        <p className="text-sm text-gray-500 mt-1">
          这将清除所有股票数据的缓存，下次访问时将获取最新数据
        </p>
      </div>
    </div>
  );
};

export default DataUpdater; 