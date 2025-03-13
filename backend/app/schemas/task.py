from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    """任务基础模型"""
    interval: int = Field(3600, description="任务执行间隔（秒）")
    is_enabled: bool = Field(True, description="任务是否启用")

class TaskCreate(TaskBase):
    """创建任务请求模型"""
    task_type: str = Field(..., description="任务类型，目前支持：update_stock_data")
    symbol: Optional[str] = Field(None, description="股票代码，如果为空则更新所有股票")

class TaskUpdate(BaseModel):
    """更新任务请求模型"""
    interval: Optional[int] = Field(None, description="任务执行间隔（秒）")
    is_enabled: Optional[bool] = Field(None, description="任务是否启用")

class TaskInfo(TaskBase):
    """任务信息响应模型"""
    task_id: str = Field(..., description="任务ID")
    description: str = Field(..., description="任务描述")
    next_run: str = Field(..., description="下次运行时间")
    last_run: Optional[str] = Field(None, description="上次运行时间")
    run_count: int = Field(0, description="运行次数")
    
    class Config:
        orm_mode = True 