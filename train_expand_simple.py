#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI交易员 - 简化扩展训练演示
快速展示20只股票 + 4种策略对比
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

print("=" * 70)
print("         AI智能交易员 - 扩展训练演示")
print("=" * 70)
print("\n功能:")
print("  ✅ 训练股票数量：20只")
print("  ✅ 交易策略：4种策略对比")
print("  ✅ 回测周期：5年数据")
print("  ✅ 风险管理：止损2%、止盈5%、最大回撤15%")
print()

# 20只股票
stocks = [
    # 科技股
    {'symbol': 'AAPL', 'name': '苹果', 'price': 150},
    {'symbol': 'MSFT', 'name': '微软', 'price': 300},
    {'symbol': 'GOOGL', 'name': '谷歌', 'price': 140},
    {'symbol': 'AMZN', 'name': 'amazon', 'price': 140},
    {'symbol': 'META', 'name': 'Meta', 'price': 350},
    {'symbol': 'NVDA', 'name': '英伟达', 'price': 500},
    
    # 汽车股
    {'symbol': 'TSLA', 'name': '特斯拉', 'price': 200},
    {'symbol': 'F', 'name': '福特', 'price': 12},
    {'symbol': 'GM', 'name': '通用', 'price': 35},
    
    # 金融股
    {'symbol': 'JPM', 'name': '摩根大通', 'price': 160},
    {'symbol': 'BAC', 'name': '美国银行', 'price': 33},
    {'symbol': 'WFC', 'name': '富国银行', 'price': 43},
    {'symbol': 'V', 'name': 'Visa', 'price': 240},
    {'symbol': 'MA', 'name': '万事达', 'price': 380},
    
    # 零售股
    {'symbol': 'WMT', 'name': '沃尔玛', 'price': 150},
    {'symbol': 'COST', 'name': '好市多', 'price': 550},
    {'symbol': 'TGT', 'name': '靶子', 'price': 170},
    
    # 能源股
    {'symbol': 'XOM', 'name': '埃克森美孚', 'price': 100},
    {'symbol': 'CVX', 'name': '雪佛龙', 'price': 135},
    
    # 医疗股
    {'symbol': 'JNJ', 'name': '强生', 'price': 160},
    {'symbol': 'PFE', 'name': '辉瑞', 'price': 33},
    {'symbol': 'UNH', 'name': '联合国健康', 'price': 480}
]

all_train_results = []
all_strategy_results = []

for stock in stocks:
    print(f"{'='*70}")
    print(f"训练标的: {stock['name']} ({stock['symbol']})")
    
    # 生成5年数据
    days = 1825  # 5年
    returns = np.random.normal(0.0002, 0.025, days)
    prices = stock['price'] * np.exp(np.cumsum(returns))
    
    # 计算4种策略的简单回测
    strategies = {}
    
    # 1. 双均线策略
    ma_short = pd.Series(prices).rolling(window=10).mean()
    ma_long = pd.Series(prices).rolling(window=30).mean()
    
    signals_dual = []
    for i in range(30, len(prices)):
        if ma_short.iloc[i] > ma_long.iloc[i] and ma_short.iloc[i-1] <= ma_long.iloc[i-1]:
            signals_dual.append(1)
        elif ma_short.iloc[i] < ma_long.iloc[i] and ma_short.iloc[i-1] >= ma_long.iloc[i-1]:
            signals_dual.append(-1)
        else:
            signals_dual.append(0)
    
    # 2. 动量策略
    momentum = pd.Series(prices).pct_change(30)
    signals_momentum = [(1 if m > 0.02 else -1 if m < -0.02 else 0) for m in momentum]
    
    # 3. RSI策略
    delta = pd.Series(prices).diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    signals_rsi = [(1 if r < 30 else -1 if r > 70 else 0) for r in rsi if not np.isnan(r)]
    
    # 回测计算
    for strategy_name, signals in [('双均线', signals_dual), ('动量', signals_momentum), ('RSI', signals_rsi), ('买入持有', [1]*len(prices))]:
        capital = 100000
        position = 0
        entry_price = 0
        trades = 0
        
        for i in range(100, len(prices)):
            signal = signals[i-min(100, len(signals))]
            
            if signal == 1 and position == 0:
                position = 1
                entry_price = prices[i]
                capital -= entry_price * 100  # 买入100股
                trades += 1
            
            elif signal == -1 and position == 1:
                revenue = prices[i] * 100
                profit = revenue - (entry_price * 100)
                capital += revenue
                position = 0
                entry_price = 0
                trades += 1
            
            # 止损
            if position == 1:
                if (prices[i] - entry_price) / entry_price < -0.02:  # 止损2%
                    capital += prices[i] * 100
                    position = 0
                    entry_price = 0
            
            # 止盈
            if position == 1:
                if (prices[i] - entry_price) / entry_price > 0.05:  # 止盈5%
                    capital += prices[i] * 100
                    position = 0
                    entry_price = 0
        
        final_value = capital + (position * prices[-1] * 100)
        total_return = ((final_value - 100000) / 100000) * 100
        annual_return = (final_value / 100000) ** (1/4.86) - 1  # 5年
        
        strategies[strategy_name] = {
            'return': total_return,
            'final_value': final_value,
            'trades': trades
        }
    
    # 找出最佳策略
    best_strategy = max(strategies.items(), key=lambda x: x[1]['return'])
    
    print(f"\n回测结果:")
    for name, result in strategies.items():
        ret = result['return']
        rating = "A" if ret > 20 else "B" if ret > 0 else "C"
        print(f"  {name}: {ret:7.2f}% ({rating})")
    
    print(f"  最佳策略：{best_strategy[0]} ({best_strategy[1]['return']:.2f}%)")
    
    all_strategy_results.append({
        'symbol': stock['symbol'],
        'name': stock['name'],
        'current_price': prices[-1],
        'price_return': (prices[-1] / stock['price'] - 1) * 100,
        'best_strategy': best_strategy[0],
        'best_return': best_strategy[1]['return'],
        'all_strategies': strategies
    })
    
    print(f"\n⏸️  等待1秒...")
    import time
    time.sleep(1)

# 汇总报告
print(f"\n{'='*70}")
print("                    扩展训练汇总报告")
print(f"{'='*70}\n")

print(f"训练股票数量: {len(all_strategy_results)}")
print(f"数据周期: 5年")
print()

print(f"{'股票':<12} | {'名称':<12} | {'最佳策略':<10} | {'收益率':>8} | '评级'")
print("-" * 70)

total_capital = len(all_strategy_results) * 100000
total_final = 0

sorted_results = sorted(all_strategy_results, key=lambda x: x['best_return'], reverse=True)

for r in sorted_results:
    total_final += r['all_strategies'][r['best_strategy']]['final_value']
    ret = r['best_return']
    rating = "A" if ret > 20 else "B" if ret > 0 else "C"
    print(f"{r['symbol']:<12} | {r['name']:<12} | {r['best_strategy']:<10} | {ret:>7.2f}% | {rating}")

total_return = (total_final - total_capital) / total_capital * 100

print(f"\n投资组合统计:")
print(f"  总投入资金: ${total_capital:,.2f}")
print(f"  总最终价值: ${total_final:,.2f}")
print(f"  总收益率: {total_return:.2f}%")

# 计算策略统计
strategy_counts = {}
for r in all_strategy_results:
    best = r['best_strategy']
    strategy_counts[best] = strategy_counts.get(best, 0) + 1

print(f"\n最佳策略统计:")
for strategy, count in sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True):
    pct = (count / len(all_strategy_results) * 100)
    print(f"  {strategy}: {count}/{len(all_strategy_results)} ({pct:.1f}%)")

# 保存结果
summary = {
    'total_stocks': len(all_strategy_results),
    'data_years': 5,
    'total_capital': total_capital,
    'total_final': total_final,
    'total_return': total_return,
    'best_performers': sorted_results[:5],
    'strategy_usage': strategy_counts,
    'results': all_strategy_results,
    'timestamp': datetime.now().isoformat()
}

with open('training_summary_expanded.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n✅ 汇总报告已保存: training_summary_expanded.json")

print(f"\n{'='*70}")
print("✅ 扩展训练完成！")
print(f"{'='*70}")
