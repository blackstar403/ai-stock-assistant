# AI股票助理

AI股票助理是一个现代化的Web应用，使用AI技术分析股票市场，提供实时数据、图表和智能投资建议，帮助用户做出更明智的投资决策。

## 功能特点

- 🔍 **股票搜索**：快速搜索全球股票市场的股票
- 📊 **实时数据**：查看股票的实时价格、涨跌幅等基本信息
- 📈 **价格图表**：查看不同时间范围的股票价格走势图
- 🤖 **AI分析**：获取基于AI的股票分析、情绪评估和投资建议
- 📚 **收藏管理**：保存感兴趣的股票，添加个人笔记
- 🌙 **深色模式**：支持浅色/深色模式，保护您的眼睛

## 技术栈

- **前端框架**：Next.js 15 + React 19
- **样式**：Tailwind CSS
- **图表**：Recharts
- **状态管理**：React Hooks
- **HTTP请求**：Axios
- **UI组件**：自定义组件库

## 开始使用

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 启动生产服务器

```bash
npm run start
```

## 项目结构

```
src/
├── app/                # Next.js应用目录
│   ├── api/            # API路由
│   ├── globals.css     # 全局样式
│   ├── layout.tsx      # 布局组件
│   └── page.tsx        # 主页面
├── components/         # React组件
│   ├── ui/             # UI组件
│   ├── StockSearch.tsx # 股票搜索组件
│   ├── StockDetail.tsx # 股票详情组件
│   ├── StockChart.tsx  # 股票图表组件
│   ├── AIAnalysis.tsx  # AI分析组件
│   └── SavedStocks.tsx # 收藏股票组件
├── lib/                # 工具函数和服务
│   └── api.ts          # API服务
└── types/              # TypeScript类型定义
    └── index.ts        # 类型定义
```

## 免责声明

本应用提供的数据和分析仅供参考，不构成投资建议。投资决策请结合个人风险承受能力和专业意见。

## 许可证

MIT
