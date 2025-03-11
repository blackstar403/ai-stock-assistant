# AI 股票助手

一个基于多数据源和多种分析模式的智能股票分析助手，帮助投资者做出更明智的投资决策。

## 项目概述

AI 股票助手是一个全栈应用程序，由后端 API 和前端界面组成。它能够获取全球和中国股票市场数据，提供技术分析、基本面分析和 AI 驱动的投资建议。

## 功能特点

- **多数据源支持**：
  - Alpha Vantage：提供全球股票市场数据
  - Tushare：专注于中国股票市场数据
  - AKShare：开源财经数据接口

- **多种分析模式**：
  - 规则计算分析：基于技术指标和基本面数据的规则计算
  - 机器学习模型分析：使用训练好的机器学习模型进行预测
  - 大语言模型分析：利用 OpenAI API 进行深度分析

- **核心功能**：
  - 股票搜索和基本信息查询
  - 历史价格数据和图表展示
  - 技术指标计算和可视化
  - AI 驱动的投资建议和风险评估
  - 用户收藏和投资组合管理

## 项目架构

### 后端 (backend/)

- **技术栈**：Python, FastAPI, SQLAlchemy, Pandas
- **主要组件**：
  - 多数据源适配器
  - AI 分析服务
  - RESTful API 接口

### 前端 (frontend/)

- **技术栈**：React, TypeScript, Ant Design, ECharts
- **主要组件**：
  - 股票搜索和详情页面
  - 交互式图表和技术指标
  - AI 分析结果展示

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
# 配置 .env 文件
python train_model.py  # 可选，训练机器学习模型
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm start
```

## 项目文档

- [后端 API 文档](backend/README.md)
- [前端开发文档](frontend/README.md)

## 后续开发计划 (TODO)

### 后端优化

- [ ] 添加用户认证和授权系统
- [ ] 实现用户投资组合管理功能
- [ ] 优化机器学习模型，提高预测准确性
- [ ] 添加更多技术指标和分析方法
- [ ] 实现数据缓存机制，提高 API 响应速度
- [ ] 添加定时任务，自动更新股票数据
- [ ] 实现回测系统，验证分析策略有效性
- [ ] 添加更多数据源支持（如 Yahoo Finance）
- [ ] 开发 WebSocket 接口，提供实时数据更新

### 前端开发

- [ ] 设计并实现用户界面
- [ ] 创建交互式股票图表组件
- [ ] 实现技术指标可视化
- [ ] 开发 AI 分析结果展示页面
- [ ] 添加用户投资组合管理界面
- [ ] 实现响应式设计，支持移动设备
- [ ] 添加多语言支持
- [ ] 实现主题切换功能（明/暗模式）

### 功能扩展

- [ ] 添加股票筛选和排序功能
- [ ] 实现股票对比分析功能
- [ ] 添加行业和板块分析
- [ ] 开发市场情绪指标
- [ ] 实现自定义分析策略
- [ ] 添加预警和通知系统
- [ ] 开发 API 使用文档和示例
- [ ] 实现数据导出功能

### 部署和运维

- [ ] 配置 Docker 和 Docker Compose
- [ ] 设置 CI/CD 流程
- [ ] 实现自动化测试
- [ ] 配置监控和日志系统
- [ ] 优化性能和扩展性
- [ ] 实现数据备份和恢复机制

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议。请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

Apache License 2.0
