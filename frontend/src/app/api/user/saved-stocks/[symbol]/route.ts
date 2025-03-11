import { NextRequest, NextResponse } from 'next/server';
import { SavedStock } from '../../../../../types';

// 引用模拟数据存储
// 注意：在实际应用中，这应该是一个数据库或其他持久化存储
// 这里为了演示，我们假设可以直接访问到上一个文件中的变量
// 在实际项目中，应该使用适当的数据存储方案
declare let savedStocks: SavedStock[];

// 删除保存的股票
export async function DELETE(
  request: NextRequest,
  { params }: { params: { symbol: string } }
) {
  const symbol = params.symbol;
  
  // 模拟网络延迟
  await new Promise((resolve) => setTimeout(resolve, 500));
  
  try {
    // 这里我们模拟删除操作
    // 在实际应用中，这应该是对数据库的操作
    // 由于我们不能直接访问上一个文件中的变量，这里只是演示逻辑
    console.log(`删除股票: ${symbol}`);
    
    // 返回成功响应
    return NextResponse.json({
      success: true,
    });
  } catch (error) {
    console.error('Error deleting saved stock:', error);
    return NextResponse.json(
      {
        success: false,
        error: '删除股票时出错',
      },
      { status: 500 }
    );
  }
} 