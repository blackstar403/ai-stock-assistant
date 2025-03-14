import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { getAIAnalysis } from '../lib/api';
import { AIAnalysis as AIAnalysisType } from '../types';
import { Bot, TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';

interface AIAnalysisProps {
  symbol: string;
}

export default function AIAnalysis({ symbol }: AIAnalysisProps) {
  const [analysis, setAnalysis] = useState<AIAnalysisType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [analysisType, setAnalysisType] = useState<'rule' | 'ml' | 'llm'>('llm');
  const [hasError, setHasError] = useState(false);

  // 使用 useCallback 包装 loadAnalysis 函数
  const loadAnalysis = useCallback(async (forceRefresh: boolean = false) => {
    if (!symbol) return;
    
    // 避免重复请求，特别是对于已经失败的请求
    if (loading && !forceRefresh) return;
    if (hasError && !forceRefresh) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await getAIAnalysis(symbol, forceRefresh, analysisType);
      if (response.success && response.data) {
        setAnalysis(response.data);
        setHasLoaded(true);
        setHasError(false);
      } else {
        setError(response.error || '加载分析失败');
        setAnalysis(null);
        setHasError(true);
      }
    } catch (err) {
      console.error('加载AI分析出错:', err);
      setError('加载分析时出错');
      setAnalysis(null);
      setHasError(true);
    } finally {
      setLoading(false);
    }
  }, [symbol, analysisType, loading, hasError]);

  // 当股票代码或分析类型变化时，只重置状态，不自动加载数据
  useEffect(() => {
    setAnalysis(null);
    setError(null);
    setHasLoaded(false);
    setHasError(false);
    
    // 移除自动加载数据的逻辑，改为手动触发
  }, [symbol, analysisType]);

  // 获取情绪图标
  const getSentimentIcon = () => {
    if (!analysis) return <Minus className="h-5 w-5" />;
    
    switch (analysis.sentiment) {
      case 'positive':
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'negative':
        return <TrendingDown className="h-5 w-5 text-red-500" />;
      default:
        return <Minus className="h-5 w-5 text-yellow-500" />;
    }
  };

  // 获取风险等级样式
  const getRiskLevelStyle = () => {
    if (!analysis) return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    
    switch (analysis.riskLevel) {
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    }
  };

  // 分析类型按钮样式
  const getAnalysisTypeButtonStyle = (type: 'rule' | 'ml' | 'llm') => {
    return type === analysisType
      ? 'bg-primary text-primary-foreground'
      : 'bg-secondary/30 text-secondary-foreground hover:bg-secondary/50';
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-xl flex items-center">
          <Bot className="mr-2 h-5 w-5" />
          AI 分析
        </CardTitle>
        {analysis && (
          <div className="flex items-center space-x-2">
            <div className="flex items-center">
              {getSentimentIcon()}
              <span className="ml-1 text-sm capitalize">
                {analysis.sentiment === 'positive'
                  ? '看涨'
                  : analysis.sentiment === 'negative'
                  ? '看跌'
                  : '中性'}
              </span>
            </div>
            <div className={`px-2 py-1 rounded-full text-xs ${getRiskLevelStyle()}`}>
              风险:&nbsp;
              {analysis.riskLevel === 'low'
                ? '低'
                : analysis.riskLevel === 'high'
                ? '高'
                : '中'}
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent>
        {/* 分析类型选择器 */}
        <div className="flex mb-4 space-x-2 border-b pb-4">
          <div className="text-sm font-medium mr-2 flex items-center">分析模式:</div>
          <div className="flex rounded-md overflow-hidden border">
            <button
              className={`px-3 py-1 text-xs font-medium ${getAnalysisTypeButtonStyle('rule')}`}
              onClick={() => setAnalysisType('rule')}
            >
              规则分析
            </button>
            <button
              className={`px-3 py-1 text-xs font-medium border-l border-r ${getAnalysisTypeButtonStyle('ml')}`}
              onClick={() => setAnalysisType('ml')}
            >
              机器学习
            </button>
            <button
              className={`px-3 py-1 text-xs font-medium ${getAnalysisTypeButtonStyle('llm')}`}
              onClick={() => setAnalysisType('llm')}
            >
              大语言模型
            </button>
          </div>
        </div>

        {loading && (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        )}
        
        {error && (
          <div className="py-4 text-red-500 text-center">
            {error}
            <div className="mt-4">
              <Button onClick={() => loadAnalysis(true)}>重试</Button>
            </div>
          </div>
        )}
        
        {!loading && !error && !hasLoaded && (
          <div className="py-8 text-center border border-dashed border-gray-200 rounded-md bg-gray-50">
            <Bot className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p className="text-muted-foreground mb-4">
              AI分析需要消耗较多资源，点击下方按钮获取分析结果
            </p>
            <Button 
              onClick={() => loadAnalysis(false)}
              className="bg-primary hover:bg-primary/90"
              size="lg"
            >
              <Bot className="mr-2 h-5 w-5" />
              获取AI分析
            </Button>
            <p className="text-xs text-muted-foreground mt-4">
              分析可能需要几秒钟时间，请耐心等待
            </p>
          </div>
        )}
        
        {!loading && !error && analysis && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              {analysis.analysisType && (
                <div className="text-xs text-muted-foreground">
                  分析方式: {
                    analysis.analysisType === 'rule' ? '规则分析' :
                    analysis.analysisType === 'ml' ? '机器学习' : '大语言模型'
                  }
                </div>
              )}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => loadAnalysis(true)}
                className="text-xs"
              >
                <RefreshCw className="mr-1 h-3 w-3" />
                刷新分析
              </Button>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">摘要</h3>
              <p className="text-muted-foreground">{analysis.summary}</p>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">关键点</h3>
              <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
                {analysis.keyPoints.map((point, index) => (
                  <li key={index}>{point}</li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">建议</h3>
              <p className="text-muted-foreground">{analysis.recommendation}</p>
            </div>
            
            <div className="text-xs text-muted-foreground pt-4 border-t border-border">
              <p>
                免责声明: 此分析仅供参考，不构成投资建议。投资决策请结合个人风险承受能力和专业意见。
              </p>
              <p className="flex items-center">
                <span>想获取更多专业分析？</span>
                <a 
                  href="/about" 
                  className="text-primary hover:underline ml-1"
                >
                  关注「AlphaBot」公众号
                </a>
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}