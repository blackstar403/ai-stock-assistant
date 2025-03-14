import React, { useState, useEffect } from 'react';
import { getAllTasks, createTask, updateTask, deleteTask, runTaskNow } from '../lib/api';
import { TaskInfo, TaskCreate } from '../types';

const TaskManager: React.FC = () => {
  const [tasks, setTasks] = useState<TaskInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState<boolean>(false);
  
  // 新任务表单状态
  const [newTask, setNewTask] = useState<TaskCreate>({
    task_type: 'update_stock_data',
    symbol: '',
    interval: 3600,
    is_enabled: true
  });

  // 加载所有任务
  const loadTasks = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getAllTasks();
      if (response.success && response.data) {
        setTasks(response.data);
      } else {
        setError(response.error || '获取任务列表失败');
      }
    } catch (err) {
      setError('获取任务列表时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 创建新任务
  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      const response = await createTask(newTask);
      if (response.success && response.data) {
        setMessage('任务创建成功');
        setShowCreateForm(false);
        // 重置表单
        setNewTask({
          task_type: 'update_stock_data',
          symbol: '',
          interval: 3600,
          is_enabled: true
        });
        // 重新加载任务列表
        loadTasks();
      } else {
        setError(response.error || '创建任务失败');
      }
    } catch (err) {
      setError('创建任务时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 更新任务状态
  const handleToggleTaskStatus = async (taskId: string, isEnabled: boolean) => {
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      const response = await updateTask(taskId, { is_enabled: !isEnabled });
      if (response.success) {
        setMessage(`任务已${!isEnabled ? '启用' : '禁用'}`);
        // 更新本地任务列表
        setTasks(tasks.map(task => 
          task.task_id === taskId ? { ...task, is_enabled: !isEnabled } : task
        ));
      } else {
        setError(response.error || '更新任务状态失败');
      }
    } catch (err) {
      setError('更新任务状态时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 删除任务
  const handleDeleteTask = async (taskId: string) => {
    if (!window.confirm('确定要删除此任务吗？')) {
      return;
    }
    
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      const response = await deleteTask(taskId);
      if (response.success) {
        setMessage(response.data?.message || '任务已删除');
        // 从本地任务列表中移除
        setTasks(tasks.filter(task => task.task_id !== taskId));
      } else {
        setError(response.error || '删除任务失败');
      }
    } catch (err) {
      setError('删除任务时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 立即运行任务
  const handleRunTaskNow = async (taskId: string) => {
    setLoading(true);
    setError(null);
    setMessage(null);
    
    try {
      const response = await runTaskNow(taskId);
      console.log(response);
      if (response.success) {
        setMessage(response.data?.message || '任务已开始运行');
      } else {
        setError(response.error || '运行任务失败');
      }
    } catch (err) {
      setError('运行任务时发生错误');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 格式化时间间隔
  const formatInterval = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds}秒`;
    } else if (seconds < 3600) {
      return `${Math.floor(seconds / 60)}分钟`;
    } else if (seconds < 86400) {
      return `${Math.floor(seconds / 3600)}小时`;
    } else {
      return `${Math.floor(seconds / 86400)}天`;
    }
  };

  // 组件加载时获取任务列表
  useEffect(() => {
    loadTasks();
  }, []);

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">定时任务管理</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          {showCreateForm ? '取消' : '创建任务'}
        </button>
      </div>
      
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
      
      {/* 创建任务表单 */}
      {showCreateForm && (
        <div className="bg-gray-50 p-4 rounded mb-6">
          <h3 className="text-lg font-medium mb-3">创建新任务</h3>
          <form onSubmit={handleCreateTask}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  任务类型
                </label>
                <select
                  value={newTask.task_type}
                  onChange={(e) => setNewTask({ ...newTask, task_type: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  disabled
                  id="task-type"
                  name="task-type"
                >
                  <option value="update_stock_data">更新股票数据</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">目前仅支持更新股票数据的任务</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  股票代码 (可选)
                </label>
                <input
                  type="text"
                  value={newTask.symbol || ''}
                  onChange={(e) => setNewTask({ ...newTask, symbol: e.target.value })}
                  placeholder="留空则更新所有股票"
                  className="w-full border rounded px-3 py-2"
                  id="task-symbol"
                  name="task-symbol"
                />
                <p className="text-xs text-gray-500 mt-1">如果留空，将更新所有股票数据</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  执行间隔 (秒)
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    value={newTask.interval}
                    onChange={(e) => setNewTask({ ...newTask, interval: parseInt(e.target.value) })}
                    min="60"
                    className="w-full border rounded px-3 py-2"
                    id="task-interval"
                    name="task-interval"
                  />
                  <span className="text-gray-500">{formatInterval(newTask.interval)}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">建议至少设置为60秒</p>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_enabled"
                  checked={newTask.is_enabled}
                  onChange={(e) => setNewTask({ ...newTask, is_enabled: e.target.checked })}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
                <label htmlFor="is_enabled" className="ml-2 block text-sm text-gray-700">
                  立即启用
                </label>
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:bg-green-300"
                >
                  {loading ? '创建中...' : '创建任务'}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
      
      {/* 任务列表 */}
      {loading && tasks.length === 0 ? (
        <div className="flex justify-center my-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : tasks.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  描述
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  间隔
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  下次运行
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tasks.map((task) => (
                <tr key={task.task_id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{task.description}</div>
                    <div className="text-xs text-gray-500">ID: {task.task_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{formatInterval(task.interval)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {new Date(task.next_run).toLocaleString()}
                    </div>
                    {task.last_run && (
                      <div className="text-xs text-gray-500">
                        上次: {new Date(task.last_run).toLocaleString()}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      task.is_enabled 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {task.is_enabled ? '已启用' : '已禁用'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleToggleTaskStatus(task.task_id, task.is_enabled)}
                        className={`${
                          task.is_enabled 
                            ? 'text-yellow-600 hover:text-yellow-900' 
                            : 'text-green-600 hover:text-green-900'
                        }`}
                      >
                        {task.is_enabled ? '禁用' : '启用'}
                      </button>
                      <button
                        onClick={() => handleRunTaskNow(task.task_id)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        立即运行
                      </button>
                      <button
                        onClick={() => handleDeleteTask(task.task_id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-4">
          <p className="text-gray-500">暂无定时任务</p>
        </div>
      )}
      
      {/* 刷新按钮 */}
      <div className="mt-4 flex justify-center">
        <button
          onClick={loadTasks}
          disabled={loading}
          className="text-blue-500 hover:text-blue-700"
        >
          {loading ? '加载中...' : '刷新任务列表'}
        </button>
      </div>
    </div>
  );
};

export default TaskManager; 