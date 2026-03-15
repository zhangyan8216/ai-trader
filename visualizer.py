#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化模块 - 生成交易分析图表
"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TradingVisualizer:
    """交易可视化器"""
    
    def __init__(self):
        """初始化可视化器"""
        plt.style.use('seaborn-darkgrid')
        logger.info("可视化器初始化完成")
    
    def plot_price_with_indicators(self, data, symbol="stock"):
        """
        绘制价格和技术指标图
        
        Args:
            data: 包含价格和技术指标的数据
            symbol: 交易标的名称
        """
        try:
            fig, axes = plt.subplots(3, 1, figsize=(14, 12))
            fig.suptitle(f'{symbol} - 价格与技术指标分析', fontsize=16)
            
            # 1. 价格和移动平均线
            ax1 = axes[0]
            ax1.plot(data.index, data['Close'], label='收盘价', linewidth=2)
            ax1.plot(data.index, data['MA20'], label='MA20', alpha=0.7)
            ax1.plot(data.index, data['MA50'], label='MA50', alpha=0.7)
            
            # 布林线
            ax1.fill_between(data.index, data['BB_Upper'], data['BB_Lower'], 
                           alpha=0.2, label='布林带')
            
            ax1.set_ylabel('价格')
            ax1.set_title('价格走势')
            ax1.legend()
            ax1.grid(True)
            
            # 2. RSI指标
            ax2 = axes[1]
            ax2.plot(data.index, data['RSI'], label='RSI', color='purple')
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='超买线')
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='超卖线')
            ax2.fill_between(data.index, 70, 100, alpha=0.1, color='red')
            ax2.fill_between(data.index, 0, 30, alpha=0.1, color='green')
            ax2.set_ylabel('RSI')
            ax2.set_title('相对强度指标')
            ax2.legend()
            ax2.grid(True)
            
            # 3. MACD指标
            ax3 = axes[2]
            ax3.plot(data.index, data['MACD'], label='MACD', linewidth=1.5)
            ax3.plot(data.index, data['MACD_Signal'], label='信号线', linewidth=1.5)
            ax3.bar(data.index, data['MACD_Diff'], label='柱状图', alpha=0.3)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax3.set_ylabel('MACD')
            ax3.set_title('指数平滑异同移动平均线')
            ax3.legend()
            ax3.grid(True)
            
            plt.tight_layout()
            filename = f"{symbol}_analysis.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"图表已保存: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"绘图时出错: {e}")
            return None
    
    def plot_backtest_results(self, results, symbol="stock"):
        """
        绘制回测结果
        
        Args:
            results: 回测结果
            symbol: 交易标的名称
        """
        try:
            if not results or 'trades' not in results:
                return None
            
            trades = results['trades']
            if not trades:
                return None
            
            # 创建资金曲线
            capital = results['initial_capital']
            capital_curve = [capital]
            
            positions = {}
            for trade in trades:
                if trade['action'] == 'buy':
                    capital -= trade['price'] * trade['shares']
                    positions['shares'] = trade['shares']
                    positions['entry_price'] = trade['price']
                else:  # sell
                    capital += trade['price'] * trade['shares']
                    positions = {}
                
                # 计算总资产
                if 'shares' in positions:
                    total_value = capital + positions['shares'] * trade['price']
                else:
                    total_value = capital
                
                capital_curve.append(total_value)
            
            # 绘图
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(capital_curve, label='总资产', linewidth=2)
            ax.axhline(y=results['initial_capital'], 
                      color='r', linestyle='--', 
                      label=f'初始资金 ${results["initial_capital"]:,.0f}')
            
            # 标记买卖点
            buy_points = [(i, t['price']) for i, t in enumerate(results['trades']) if t['action'] == 'buy']
            sell_points = [(i, t['price']) for i, t in enumerate(results['trades']) if t['action'] == 'sell']
            
            if buy_points:
                ax.scatter([p[0] for p in buy_points], [p[1] for p in buy_points],
                          color='g', marker='^', s=100, label='买入', zorder=5)
            if sell_points:
                ax.scatter([p[0] for p in sell_points], [p[1] for p in sell_points],
                          color='r', marker='v', s=100, label='卖出', zorder=5)
            
            ax.set_xlabel('交易次数')
            ax.set_ylabel('总资产 ($)')
            ax.set_title(f'{symbol} - 回测资金曲线\n'
                        f'初始资金: ${results["initial_capital"]:,.2f} | '
                        f'最终价值: ${results["final_value"]:,.2f} | '
                        f'收益率: {results["total_return"]:.2f}%')
            ax.legend()
            ax.grid(True)
            
            plt.tight_layout()
            filename = f"{symbol}_backtest.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"回测图表已保存: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"绘制回测结果时出错: {e}")
            return None
    
    def create_interactive_chart(self, data, symbol="stock"):
        """
        创建交互式图表 (使用Plotly)
        
        Args:
            data: 价格数据
            symbol: 交易标的名称
        """
        try:
            fig = go.Figure()
            
            # 添加价格线
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='收盘价',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # 添加移动平均线
            if 'MA20' in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data['MA20'],
                    mode='lines',
                    name='MA20',
                    line=dict(color='orange', width=1.5)
                ))
            
            if 'MA50' in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data['MA50'],
                    mode='lines',
                    name='MA50',
                    line=dict(color='green', width=1.5)
                ))
            
            # 更新布局
            fig.update_layout(
                title=f'{symbol} - 交互式价格图表',
                xaxis_title='日期',
                yaxis_title='价格',
                hovermode='x unified',
                template='plotly_dark',
                height=600
            )
            
            filename = f"{symbol}_interactive.html"
            fig.write_html(filename)
            
            logger.info(f"交互式图表已保存: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"创建交互式图表时出错: {e}")
            return None


def main():
    """测试可视化功能"""
    import yfinance as yf
    
    print("测试可视化模块...")
    
    # 获取测试数据
    data = yf.Ticker('AAPL').history(period='6m')
    
    # 计算技术指标
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['RSI'] = data['Close'].rolling(window=14).mean()
    data['MACD'] = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()
    data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
    data['MACD_Diff'] = data['MACD'] - data['MACD_Signal']
    data['BB_Middle'] = data['Close'].rolling(window=20).mean()
    data['BB_Std'] = data['Close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2)
    data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2)
    
    # 创建可视化器
    visualizer = TradingVisualizer()
    
    # 生成图表
    visualizer.plot_price_with_indicators(data, 'AAPL')
    visualizer.create_interactive_chart(data, 'AAPL')
    
    print("✅ 可视化测试完成")


if __name__ == '__main__':
    main()
