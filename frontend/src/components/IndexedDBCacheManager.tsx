import React, { useState, useEffect } from 'react';
import { indexedDBCache, CacheStats } from '../lib/indexedDBCache';

const IndexedDBCacheManager: React.FC = () => {
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [pattern, setPattern] = useState<string>('');
  const [message, setMessage] = useState<string | null>(null);

  // 加载缓存统计信息
  const loadCacheStats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const stats = await indexedDBCache.getStats();
      setCacheStats(stats);
    } catch (err) {
      setError('获取缓存统计信息时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 清空所有缓存
  const handleClearCache = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      await indexedDBCache.clear();
      setMessage('缓存已成功清空');
      loadCacheStats(); // 重新加载统计信息
    } catch (err) {
      setError('清空缓存时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 清除匹配模式的缓存
  const handleClearPattern = async () => {
    if (!pattern.trim()) {
      setError('请输入有效的模式');
      return;
    }
    
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      const count = await indexedDBCache.clearPattern(pattern);
      setMessage(`已成功清除匹配 &quot;${pattern}&quot; 的 ${count} 个缓存项`);
      setPattern(''); // 清空输入
      loadCacheStats(); // 重新加载统计信息
    } catch (err) {
      setError('清除缓存模式时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 清理过期缓存
  const handleCleanupCache = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      const count = await indexedDBCache.cleanup();
      setMessage(`已成功清理 ${count} 个过期缓存项`);
      loadCacheStats(); // 重新加载统计信息
    } catch (err) {
      setError('清理过期缓存时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 组件加载时获取缓存统计信息
  useEffect(() => {
    // 确保IndexedDB已初始化
    indexedDBCache.init().then(() => {
      loadCacheStats();
    }).catch(err => {
      setError('初始化缓存服务时发生错误');
      console.error(err);
    });
  }, []);

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">IndexedDB 缓存管理</h2>
      
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
      
      {/* 缓存统计信息 */}
      {loading ? (
        <div className="flex justify-center my-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : cacheStats ? (
        <div className="mb-6">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-500">总缓存项</p>
              <p className="text-2xl font-bold">{cacheStats.totalItems}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-500">活跃缓存项</p>
              <p className="text-2xl font-bold">{cacheStats.activeItems}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-500">过期缓存项</p>
              <p className="text-2xl font-bold">{cacheStats.expiredItems}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <button 
                onClick={loadCacheStats}
                className="text-blue-500 hover:text-blue-700"
                disabled={loading}
              >
                刷新统计
              </button>
            </div>
          </div>
          
          {/* 缓存键列表 */}
          {cacheStats.cacheKeys.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-medium mb-2">缓存键列表</h3>
              <div className="max-h-60 overflow-y-auto bg-gray-50 p-3 rounded">
                {cacheStats.cacheKeys.map((key, index) => (
                  <div key={index} className="text-sm py-1 border-b border-gray-200 last:border-0">
                    {key}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <p>无法获取缓存统计信息</p>
      )}
      
      {/* 缓存操作 */}
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium mb-2">清除特定模式的缓存</h3>
          <div className="flex space-x-2">
            <input
              type="text"
              value={pattern}
              onChange={(e) => setPattern(e.target.value)}
              placeholder="输入缓存键模式"
              className="flex-1 border rounded px-3 py-2"
              id="indexeddb-cache-pattern"
              name="indexeddb-cache-pattern"
            />
            <button
              onClick={handleClearPattern}
              disabled={loading || !pattern.trim()}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-blue-300"
            >
              清除
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            例如: "get_stock_info" 将清除所有包含该字符串的缓存项
          </p>
        </div>
        
        <div className="flex space-x-4">
          <button
            onClick={handleCleanupCache}
            disabled={loading}
            className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 disabled:bg-yellow-300"
          >
            清理过期缓存
          </button>
          
          <button
            onClick={handleClearCache}
            disabled={loading}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:bg-red-300"
          >
            清空所有缓存
          </button>
        </div>
      </div>
    </div>
  );
};

export default IndexedDBCacheManager; 