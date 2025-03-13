'use client';

import React, { useState } from 'react';
import IndexedDBCacheManager from '../../components/IndexedDBCacheManager';
import TaskManager from '../../components/TaskManager';
import DataUpdater from '../../components/DataUpdater';

const SystemPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'cache' | 'tasks' | 'data'>('cache');

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">系统管理</h1>
      
      {/* 标签页导航 */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex -mb-px">
          <button
            onClick={() => setActiveTab('cache')}
            className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
              activeTab === 'cache'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            缓存管理
          </button>
          <button
            onClick={() => setActiveTab('tasks')}
            className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
              activeTab === 'tasks'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            定时任务
          </button>
          <button
            onClick={() => setActiveTab('data')}
            className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
              activeTab === 'data'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            数据更新
          </button>
        </nav>
      </div>
      
      {/* 标签页内容 */}
      <div>
        {activeTab === 'cache' && <IndexedDBCacheManager />}
        {activeTab === 'tasks' && <TaskManager />}
        {activeTab === 'data' && <DataUpdater />}
      </div>
    </div>
  );
};

export default SystemPage; 