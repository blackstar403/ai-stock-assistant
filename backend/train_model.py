"""
运行模型训练脚本
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.utils.train_model import train_models

if __name__ == "__main__":
    print("开始训练股票分析模型...")
    train_models()
    print("模型训练完成！") 