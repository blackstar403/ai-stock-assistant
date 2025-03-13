import asyncio
import time
from typing import Dict, Any, List, Callable, Awaitable, Optional
from datetime import datetime, timedelta
import logging
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("scheduler")

class Task:
    """定时任务"""
    def __init__(
        self, 
        task_id: str,
        func: Callable[..., Awaitable[Any]], 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None,
        interval: int = 3600,  # 默认1小时
        next_run: float = None,
        description: str = "",
        is_enabled: bool = True
    ):
        self.task_id = task_id
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.interval = interval
        self.next_run = next_run or time.time()
        self.description = description
        self.is_enabled = is_enabled
        self.last_run = None
        self.last_result = None
        self.last_error = None
        self.run_count = 0

class SchedulerService:
    """定时任务调度服务"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchedulerService, cls).__new__(cls)
            cls._instance._tasks: Dict[str, Task] = {}
            cls._instance._running = False
            cls._instance._task_loop = None
        return cls._instance
    
    def add_task(
        self, 
        func: Callable[..., Awaitable[Any]], 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None,
        interval: int = 3600,
        description: str = "",
        task_id: str = None,
        is_enabled: bool = True
    ) -> str:
        """添加定时任务"""
        task_id = task_id or str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            interval=interval,
            description=description,
            is_enabled=is_enabled
        )
        
        self._tasks[task_id] = task
        logger.info(f"添加任务: {task_id} - {description}")
        return task_id
    
    def remove_task(self, task_id: str) -> bool:
        """移除定时任务"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            logger.info(f"移除任务: {task_id}")
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "description": task.description,
            "interval": task.interval,
            "next_run": datetime.fromtimestamp(task.next_run).isoformat(),
            "last_run": datetime.fromtimestamp(task.last_run).isoformat() if task.last_run else None,
            "run_count": task.run_count,
            "is_enabled": task.is_enabled
        }
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务信息"""
        return [self.get_task(task_id) for task_id in self._tasks]
    
    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        if task_id in self._tasks:
            self._tasks[task_id].is_enabled = True
            logger.info(f"启用任务: {task_id}")
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        if task_id in self._tasks:
            self._tasks[task_id].is_enabled = False
            logger.info(f"禁用任务: {task_id}")
            return True
        return False
    
    def update_task_interval(self, task_id: str, interval: int) -> bool:
        """更新任务间隔"""
        if task_id in self._tasks:
            self._tasks[task_id].interval = interval
            logger.info(f"更新任务间隔: {task_id} - {interval}秒")
            return True
        return False
    
    async def run_task_now(self, task_id: str) -> bool:
        """立即运行任务"""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        
        try:
            logger.info(f"手动运行任务: {task_id} - {task.description}")
            task.last_result = await task.func(*task.args, **task.kwargs)
            task.last_run = time.time()
            task.run_count += 1
            task.last_error = None
            return True
        except Exception as e:
            task.last_error = str(e)
            logger.error(f"任务执行出错: {task_id} - {str(e)}")
            return False
    
    async def _run_scheduler(self):
        """运行调度器"""
        self._running = True
        logger.info("启动调度器")
        
        while self._running:
            current_time = time.time()
            
            # 查找需要运行的任务
            for task_id, task in self._tasks.items():
                if not task.is_enabled:
                    continue
                
                if current_time >= task.next_run:
                    try:
                        logger.info(f"运行任务: {task_id} - {task.description}")
                        task.last_result = await task.func(*task.args, **task.kwargs)
                        task.last_run = current_time
                        task.run_count += 1
                        task.next_run = current_time + task.interval
                        task.last_error = None
                    except Exception as e:
                        task.last_error = str(e)
                        logger.error(f"任务执行出错: {task_id} - {str(e)}")
                        # 即使出错，也更新下次运行时间
                        task.next_run = current_time + task.interval
            
            # 等待一段时间再检查
            await asyncio.sleep(1)
    
    def start(self):
        """启动调度器"""
        if not self._running:
            self._task_loop = asyncio.create_task(self._run_scheduler())
            logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if self._running:
            self._running = False
            if self._task_loop:
                self._task_loop.cancel()
            logger.info("调度器已停止")
    
    def is_running(self) -> bool:
        """检查调度器是否运行中"""
        return self._running 