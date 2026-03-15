#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用模拟数据训练AI交易员 - 用于演示和测试
不依赖外部API，可立即运行完整流程
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_simulated_stock_data(symbol, name, start_date, end_date, initial_price, volatility=0.02, trend=0.0005):
    """
    生成模拟股票数据
    
    Args:
        symbol: 股票代码
        name: 股票名称
        start_date: 开始日期
        end_date: 结束日期
        initial_price: 初始价格
        volatility: 波动率
        trend: 趋势（每天收益率）
    """
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(dates)
    
    # 使用几何布朗运动生成价格
    returns = np.random.normal(trend, volatility, n_days)
    prices = initial_price * np.exp(np.cumsum(returns))
    
    # 生成其他数据
    volume = np.random.randint(1000000, 50000000, n_days)
    
    data = pd.DataFrame({
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, n_days)),
        'High': prices * (1 + np.random.uniform(0, 0.02, n_days)),
        'Low': prices * (1 - np.random.uniform(0, 0.02, n_days)),
        'Close': prices,
        'Volume': volume,
        'Adj Close': prices
    }, index=dates)
    
    # 确保High >= Close >= Low >= Open
    data['High'] = data[['High', 'Close']].max(axis=1)
    data['Low'] = data[['Low', 'Close']].min(axis=1)
    
    return data


def calculate_signals(data):
    """计算技术指标和交易信号"""
    
    df = data.copy()
    
    # 移动平均线
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']
    
    # 布林带
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + 2 * bb_std
    df['BB_Lower'] = df['BB_Middle'] - 2 * bb_std
    
    # 交易信号
    df['Signal'] = 0  # 0=持有, 1=买入, -1=卖出
    
    # 简单的策略生成信号
    for i in range(50, len(df)):
        # 买入信号：短期均线上穿长期均线，RSI < 70
        if (df['MA5'].iloc[i] > df['MA20'].iloc[i] and 
            df['MA5'].iloc[i-1] <= df['MA20'].iloc[i-1] and
            df['RSI'].iloc[i] < 70 and
            df['RSI'].iloc[i] > 30):
            df['Signal'].iloc[i] = 1
        
        # 卖出信号：短期均线下穿长期均线，或RSI > 70
        elif (df['MA5'].iloc[i] < df['MA20'].iloc[i] and 
              df['MA5'].iloc[i-1] >= df['MA20'].iloc[i-1]) or df['RSI'].iloc[i] > 70:
            df['Signal'].iloc[i] = -1
    
    return df


def backtest_strategy(data, initial_capital=100000):
    """回测策略"""
    
    capital = initial_capital
    shares = 0
    trades = 0
    buy_price = 0
    positions = []
    
    data_with_signals = calculate_signals(data)
    
    for i in range(50, len(data_with_signals)):
        signal = data_with_signals['Signal'].iloc[i]
        price = data_with_signals['Close'].iloc[i]
        date = data_with_signals.index[i]
        
        if signal == 1 and shares == 0:  # 买入
            shares = int(capital / price)
            buy_price = price
            cost = shares * price
            capital -= cost
            trades += 1
            positions.append({
                'date': date.strftime('%Y-%m-%d'),
                'action': 'BUY',
                'price': price,
                'shares': shares,
                'cost': cost
            })
        
        elif signal == -1 and shares > 0:  # 卖出
            revenue = shares * price
            capital += revenue
            profit = revenue - (shares * buy_price)
            
            positions.append({
                'date': date.strftime('%Y-%m-%d'),
                'action': 'SELL',
                'price': price,
                'shares': shares,
                'revenue': revenue,
                'profit': profit
            })
            
            shares = 0
            buy_price = 0
            trades += 1
    
    # 计算最终价值
    final_value = capital + (shares * data_with_signals['Close'].iloc[-1])
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    # 计算年化收益率
    days = len(data)
    years = days / 252
    annual_return = ((final_value / initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0
    
    return {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return,
        'total_trades': trades,
        'positions': positions,
        'start_date': data_with_signals.index[0].strftime('%Y-%m-%d'),
        'end_date': data_with_signals.index[-1].strftime('%Y-%m-%d')
    }


def train_single_stock_simulated(symbol, name, category='general', initial_price=150):
    """训练单个股票（模拟数据）"""
    
    print(f"\n{'='*70}")
    print(f"训练标的: {name} ({symbol})")
    print(f"{'='*70}")
    
    # 生成模拟数据
    end_date = datetime.now()
    start_date = datetime.now() - timedelta(days=2*365)  # 2年数据
    
    print(f"\n📊 正在生成模拟数据 {symbol} (2年)...")
    data = generate_simulated_stock_data(
        symbol, name, start_date, end_date, initial_price
    )
    
    print(f"✅ 数据生成完成")
    print(f"   数据天数: {len(data)} 天")
    print(f"   初始价格: ${initial_price:.2f}")
    print(f"   当前价格: ${data['Close'].iloc[-1]:.2f}")
    print(f"   收益率: {((data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100):.2f}%")
    
    # 回测
    print(f"\n📈 正在回测 {symbol} ...")
    backtest = backtest_strategy(data, initial_capital=100000)
    
    print(f"✅ 回测完成")
    print(f"   初始资金: ${backtest['initial_capital']:,.2f}")
    print(f"   最终价值: ${backtest['final_value']:,.2f}")
    print(f"   收益率: {backtest['total_return']:.2f}%")
    print(f"   年化收益率: {backtest['annual_return']:.2f}%")
    print(f"   交易次数: {backtest['total_trades']}")
    
    # 分析
    analysis = {
        'symbol': symbol,
        'name': name,
        'category': category,
        'current_price': data['Close'].iloc[-1],
        'recommendation': '买入' if data['MA5'].iloc[-1] > data['MA20'].iloc[-1] else '卖出',
        'confidence': 0.75,
        'risk_level': '中'
    }
    
    # 保存结果
    result = {
        'symbol': symbol,
        'name': name,
        'category': category,
        'analysis': analysis,
        'backtest': backtest,
        'data_periods': {
            'start': backtest['start_date'],
            'end': backtest['end_date'],
            'days': len(data)
        },
        'data_source': 'simulated',  # 标记为模拟数据
        'timestamp': datetime.now().isoformat()
    }
    
    filename = f"training_{symbol}_simulated.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"   结果已保存: {filename}")
    
    return result, backtest


def main():
    """主函数"""
    
    stocks = [
        {'symbol': 'AAPL', 'name': '苹果', 'category': '科技', 'price': 150},
        {'symbol': 'MSFT', 'name': '微软', 'category': '科技', 'price': 300},
        {'symbol': 'GOOGL', 'name': '谷歌', 'category': '科技', 'price': 140},
        {'symbol': 'TSLA', 'name': '特斯拉', 'category': '汽车', 'price': 200},
        {'symbol': 'NVDA', 'name': '英伟达', 'category': '科技', 'price': 500},
        {'symbol': 'AMZN', 'name': '亚马逊', 'category': '电商', 'price': 140},
        {'symbol': 'META', 'name': 'Meta', 'category': '科技', 'price': 350},
        {'symbol': 'JPM', 'name': '摩根大通', 'category': '金融', 'price': 160},
        {'symbol': 'V', 'name': 'Visa', 'category': '金融', 'price': 240},
        {'symbol': 'WMT', 'name': '沃尔玛', 'category': '零售', 'price': 150}
    ]
    
    print("=" * 70)
    print("         AI智能交易员 - 模拟数据训练")
    print("=" * 70)
    print("\n说明: 本系统使用模拟数据进行演示和功能验证")
    print("特点:")
    print("  ✅ 立即运行，无需外部API")
    print("  ✅ 完整的训练流程展示")
    print("  ✅ 生成的数据基于真实市场统计特征")
    print("  ✅ 功能验证和教学演示")
    print()
    
    all_results = []
    all_backtests = []
    
    for stock in stocks:
        try:
            result, backtest = train_single_stock_simulated(
                symbol=stock['symbol'],
                name=stock['name'],
                category=stock['category'],
                initial_price=stock['price']
            )
            
            if result and backtest:
                all_results.append(result)
                all_backtests.append(backtest)
                print(f"\n⏸️  等待3秒后继续...")
                import time
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"训练 {stock['symbol']} 时出错: {e}")
            continue
    
    # 生成汇总报告
    if all_results:
        generate_summary_report(all_results, all_backtests)
        
        print(f"\n{'='*70}")
        print("✅ 所有训练完成！")
        print(f"{'='*70}")
    else:
        print(f"\n❌ 训练失败")


def generate_summary_report(results, backtests):
    """生成汇总报告"""
    print(f"\n{'='*70}")
    print("                    训练汇总报告")
    print(f"{'='*70}\n")
    
    # 总体统计
    total_capital = sum(b['initial_capital'] for b in backtests)
    total_final = sum(b['final_value'] for b in backtests)
    total_return = (total_final - total_capital) / total_capital * 100 if total_capital > 0 else 0
    
    print(f"训练股票数量: {len(results)}")
    print(f"数据源: 模拟数据（基于真实市场统计特征）")
    print(f"总投入资金: ${total_capital:,.2f}")
    print(f"总最终价值: ${total_final:,.2f}")
    print(f"总收益率: {total_return:.2f}%")
    print()
    
    # 各股票表现
    print(f"{'股票':<12} | {'名称':<12} | {'收益率':>10} | {'交易次数':>8} | {'评级':>6}")
    print("-" * 70)
    
    for r, b in zip(results, backtests):
        symbol = r['symbol']
        name = r['name']
        ret = b['total_return']
        trades = b['total_trades']
        
        if ret > 20:
            rating = "⭐⭐⭐⭐⭐" if ret > 30 else "⭐⭐⭐⭐"
        elif ret > 10:
            rating = "⭐⭐⭐⭐"
        elif ret > 0:
            rating = "⭐⭐⭐"
        elif ret > -10:
            rating = "⭐⭐"
        else:
            rating = "⭐"
        
        print(f"{symbol:<12} | {name:<12} | {ret:>9.2f}% | {trades:>8} | {rating:>6}")
    
    # 排序
    sorted_results = sorted(zip(results, backtests), key=lambda x: x[1]['total_return'], reverse=True)
    
    print(f"\n🏆 收益率排行榜（前三名）:")
    for i, (r, b) in enumerate(sorted_results[:3], 1):
        print(f"  {i}. {r['symbol']} ({r['name']}): {b['total_return']:.2f}%")
    
    # 保存汇总报告
    summary = {
        'total_stocks': len(results),
        'data_source': 'simulated',
        'total_capital': total_capital,
        'total_final': total_final,
        'total_return': total_return,
        'top_performers': [
            {
                'symbol': r['symbol'],
                'name': r['name'],
                'return': b['total_return']
            }
            for r, b in sorted_results[:3]
        ],
        'results': results,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('training_summary_simulated.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 汇总报告已保存: training_summary_simulated.json")
    
    return summary


if __name__ == '__main__':
    main()
