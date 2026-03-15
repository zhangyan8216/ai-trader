#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI交易员 - 简洁迭代优化"""
import json, numpy as np, pandas as pd, sys
from datetime import datetime

def main():
    print("=" * 70)
    print("         AI智能交易员 - 迭代优化训练")
    print("=" * 70)
    
    # 参数测试
    stop_losses = [0.01, 0.02, 0.03]
    take_profits = [0.05, 0.08, 0.]
    strategies = ['双均线', '动量', 'RSi']
    
    stocks = [
        {'symbol': 'AAPL', 'price': 150},
        {'symbol': 'MSFT', 'price': 300},
        {'symbol': 'NVDA', 'price': 500},
        {'symbol': 'JPM', 'price': 160},
        {'symbol': 'TSLA', 'price': 200},
        {'symbol': 'META', 'price': 350}
    ]
    
    print(f"\n搜索空间: {len(stop_losses) * len(take_profits) * len(strategies)} 种组合")
    print(f"\n开始优化...\n")
    
    best_return = -999
    best_params = {}
    
    for stock in stocks:
        days = 1825
        returns = np.random.normal(0.0003, 0.03, days)
        prices = stock['price'] * np.exp(np.cumsum(returns))
        
        stock_best = -999
        
        for sl in stop_losses:
            for tp in take_profits:
                for s in strategies:
                    # 简化回测
                    capital = 100000
                    shares = 0
                    entry_price = 0
                    
                    for i in range(50, len(prices)):
                        if prices[i] > prices[i-50] * 1.05:  # 简化信号
                            if shares == 0:
                                shares = int(capital / prices[i])
                                capital -= shares * prices[i]
                                entry_price = prices[i]
                        
                        if shares > 0 and (prices[i] / entry_price < 1-sl or prices[i] / entry_price > 1+tp):
                            capital += shares * prices[i]
                            shares = 0
                    
                    total_return = ((capital - 100000) / 100000) * 100
                    
                    if total_return > stock_best:
                        stock_best = total_return
                        best_params = {'sl': sl, 'tp': tp, 's': s}
        
        if stock_best > best_return:
            best_return = stock_best
    print(f"{stock['symbol']:6} 最佳: {stock_best:.2f}%")
    
    print(f"\n最终最佳收益: {best_return:.2f}%")
    
    # 保存报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'best_return': best_return,
        'best_params': best_params,
        'stocks': stocks
    }
    
    with open('optimization_simple.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ 优化完成！结果已保存")

if __name__ == '__main__':
    main()
