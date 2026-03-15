#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI交易员 - 扩展训练版本
包含：更多股票、多种策略、参数优化
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TradingStrategy:
    """交易策略类"""
    
    @staticmethod
    def momentum_strategy(data, short_days=10, long_days=30):
        """动量策略"""
        df = data.copy()
        
        # 计算动量
        df['momentum_short'] = df['Close'].pct_change(short_days)
        df['momentum_long'] = df['Close'].pct_change(long_days)
        
        # 动量信号
        df['signal'] = 0
        df.loc[(df['momentum_short'] > 0.02) & (df['momentum_long'] > 0), 'signal'] = 1
        df.loc[(df['momentum_short'] < -0.02) & (df['momentum_long'] < -0.02), 'signal'] = -1
        
        return df
    
    @staticmethod
    def mean_reversion_strategy(data, window=20, std_dev=2):
        """均值回归策略"""
        df = data.copy()
        
        # 计算移动平均和标准差
        df['mean'] = df['Close'].rolling(window=window).mean()
        df['std'] = df['Close'].rolling(window=window).std()
        df['z_score'] = (df['Close'] - df['mean']) / df['std']
        
        # 均值回归信号
        df['signal'] = 0
        df.loc[df['z_score'] < -std_dev, 'signal'] = 1  # 价格低于均值，买入
        df.loc[df['z_score'] > std_dev, 'signal'] = -1  # 价格高于均值，卖出
        
        return df
    
    @staticmethod
    def dual_moving_average_strategy(data, fast=10, slow=30):
        """双均线策略"""
        df = data.copy()
        
        # 计算快慢均线
        df['ma_fast'] = df['Close'].rolling(window=fast).mean()
        df['ma_slow'] = df['Close'].rolling(window=slow).mean()
        
        # 交叉信号
        df['signal'] = 0
        for i in range(len(df)):
            if i >= slow:
                if df['ma_fast'].iloc[i] > df['ma_slow'].iloc[i] and df['ma_fast'].iloc[i-1] <= df['ma_slow'].iloc[i-1]:
                    df['signal'].iloc[i] = 1  # 金叉，买入
                elif df['ma_fast'].iloc[i] < df['ma_slow'].iloc[i] and df['ma_fast'].iloc[i-1] >= df['ma_slow'].iloc[i-1]:
                    df['signal'].iloc[i] = -1  # 死叉，卖出
        
        return df
    
    @staticmethod
    def rsi_strategy(data, period=14, oversold=30, overbought=70):
        """RSI策略"""
        df = data.copy()
        
        # 计算RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # RSI信号
        df['signal'] = 0
        df.loc[df['rsi'] < oversold, 'signal'] = 1  # 超卖，买入
        df.loc[df['rsi'] > overbought, 'signal'] = -1  # 超买，卖出
        
        return df


def generate_simulated_data(symbol, name, start_date, end_date, initial_price, volatility=0.02, trend=0.0002):
    """生成模拟数据"""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(dates)
    
    returns = np.random.normal(trend, volatility, n_days)
    prices = initial_price * np.exp(np.cumsum(returns))
    
    volume = np.random.randint(1000000, 50000000, n_days)
    
    data = pd.DataFrame({
        'Open': prices * (1 + np.random.uniform(-0.005, 0.005, n_days)),
        'High': prices * (1 + np.random.uniform(0, 0.015, n_days)),
        'Low': prices * (1 - np.random.uniform(0, 0.015, n_days)),
        'Close': prices,
        'Volume': volume,
        'Adj Close': prices
    }, index=dates)
    
    data['High'] = data[['High', 'Close']].max(axis=1)
    data['Low'] = data[['Low', 'Close']].min(axis=1)
    
    return data


def backtest_strategy(data, strategy_name, strategy_func, initial_capital=100000, 
                       stop_loss=0.02, take_profit=0.05, max_drawdown=0.15):
    """回测策略"""
    
    signals_df = strategy_func(data)
    
    capital = initial_capital
    shares = 0
    trades = 0
    buy_price = 0
    peak_value = initial_capital
    
    results = []
    
    for i in range(50, len(signals_df)):
        signal = signals_df['signal'].iloc[i]
        price = signals_df['Close'].iloc[i]
        
        if signal == 1 and shares == 0:
            # 买入
            shares = int(capital / price)
            buy_price = price
            cost = shares * price
            capital -= cost
            trades += 1
            
        elif signal == -1 and shares > 0:
            # 卖出
            revenue = shares * price
            profit = revenue - (shares * buy_price)
            capital += revenue
            trades += 1
            
            # 更新峰值
            current_value = capital
            if current_value > peak_value:
                peak_value = current_value
            
            # 记录交易
            results.append({
                'action': 'sell',
                'price': price,
                'profit': profit,
                'value': current_value
            })
            
            shares = 0
            buy_price = 0
        
        # 检查止损
        if shares > 0:
            current_value = capital + (shares * price)
            if (price - buy_price) / buy_price <= -stop_loss:
                # 触发止损
                revenue = shares * price
                capital += revenue
                results.append({
                    'action': 'sell_stoploss',
                    'price': price,
                    'profit': revenue - (shares * buy_price),
                    'value': capital
                })
                shares = 0
                buy_price = 0
            
            elif (price - buy_price) / buy_price >= take_profit:
                # 触发止盈
                revenue = shares * price
                capital += revenue
                results.append({
                    'action': 'sell_takeprofit',
                    'price': price,
                    'profit': revenue - (shares * buy_price),
                    'value': capital
                })
                shares = 0
                buy_price = 0
            
            current_value = capital + (shares * price)
            # 检查最大回撤
            if current_value < peak_value:
                drawdown = (peak_value - current_value) / peak_value
                if drawdown > max_drawdown:
                    # 触发最大回撤止损
                    revenue = shares * price
                    capital += revenue
                    results.append({
                        'action': 'sell_drawdown',
                        'price': price,
                        'profit': revenue - (shares * buy_price),
                        'value': capital
                    })
                    shares = 0
                    buy_price = 0
    
    # 最终价值
    final_value = capital + (shares * signals_df['Close'].iloc[-1])
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    # 计算年化收益率
    days = len(data)
    years = days / 252
    annual_return = ((final_value / initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0
    
    # 计算夏普比率（简化版）
    returns_list = [r['profit'] for r in results if r['profit'] is not None]
    if returns_list:
        avg_return = np.mean(returns_list)
        std_return = np.std(returns_list)
        sharpe_ratio = (avg_return / std_return) * (252**0.5) if std_return > 0 else 0
    else:
        sharpe_ratio = 0
    
    return {
        'strategy_name': strategy_name,
        'initial_capital': initial_capital,
        'final_value': final_value,
        'title': total_return,
        'annual_return': annual_return,
        'total_trades': trades,
        'sharpe_ratio': sharpe_ratio,
        'positions': results
    }


def train_stock_with_multiple_strategies(symbol, name, initial_price):
    """使用多种策略训练单个股票"""
    
    print(f"\n{'='*70}")
    print(f"训练标的: {name} ({symbol})")
    print(f"{'='*70}")
    
    # 生成数据
    end_date = datetime.now()
    start_date = datetime.now() - timedelta(days=5*365)  # 5年数据
    
    data = generate_simulated_data(symbol, name, start_date, end_date, initial_price)
    
    print(f"\n📊 数据生成完成:")
    print(f"   数据天数: {len(data)} 天 (5年)")
    print(f"   初始价格: ${initial_price:.2f}")
    print(f"   当前价格: ${data['Close'].iloc[-1]:.2f}")
    print(f"   价格变动: {((data['Close'].iloc[-1] / data['close'].iloc[0] - 1) * 100):.2f}%")
    
    # 测试多种策略
    strategies = {
        '双均线': lambda d: TradingStrategy.dual_moving_average_strategy(d, 10, 30),
        '动量': lambda d: TradingStrategy.momentum_strategy(d, 10, 30),
        '均值回归': lambda d: TradingStrategy.mean_reversion_strategy(d, 20, 2),
        'RSI': lambda d: TradingStrategy.rsi_strategy(d, 14, 30, 70)
    }
    
    results = {}
    
    print(f"\n📈 开始策略回测...")
    for strategy_name, strategy_func in strategies.items():
        try:
            result = backtest_strategy(data, strategy_name, strategy_func)
            results[strategy_name] = result
            
            print(f"\n  {strategy_name}策略:")
            print(f"    收益率: {result['title']:.2f}%")
            print(f"    年化收益: {result['annual_return']:.2f}%")
            print(f"    交易次数: {result['total_trades']}")
            print(f"    夏普比率: {result['share_ratio']:.2f}")
            
        except Exception as e:
            logger.error(f"{strategy_name}策略回测失败: {e}")
    
    # 策略对比
    print(f"\n🏆 策略对比:")
    sorted_strategies = sorted(results.items(), key=lambda x: x[1]['title'], reverse=True)
    
    print(f"{'策略':<12} | {'收益率':>10} | {'年化收益':>10} | {'夏普比':>8} | {'评级':>4}")
    print("-" * 60)
    
    for name, result in sorted_strategies:
        ret = result['title']
        rating = "A" if ret > 20 else "B" if ret > 0 else "C"
        print(f"{name:<12} | {ret:>9.2f}% | {result['annual_return']:>9.2f}% | {result['sharpe_ratio']:>8.2f} | {rating:>4}")
    
    return {
        'symbol': symbol,
        'name': name,
        'results': results
    }


def main():
    """主函数"""
    
    # 扩展的股票列表（20只股票）
    stocks = [
        # 大型科技公司
        {'symbol': 'AAPL', 'name': '苹果', 'price': 150},
        {'symbol': 'MSFT', 'name': '微软', 'price': 300},
        {'symbol': 'GOOGL', 'name': '谷歌', 'price': 140},
        {'symbol': 'AMZN', 'name': '亚马逊', 'price': 140},
        {'symbol': 'META', 'name': 'Meta', 'price': 350},
        {'symbol': 'NVDA', 'name': '英伟达', 'name': 500},
        
        # 汽车行业
        {'symbol': 'TSLA', 'name': '特斯拉', 'price': 200},
        {'symbol': 'F', 'name': '福特', 'price': 12},
        {'symbol': 'GM', 'name': '通用汽车', 'price': 35},
        
        # 金融行业
        {'symbol': 'JPM', 'name': '摩根大通', 'price': 160},
        {'symbol': 'BAC', 'name': '美国银行', 'price': 33},
        {'symbol': 'WFC', 'name': '富国银行', 'name': 43},
        {'symbol': 'V', 'name': 'Visa', 'price': 240},
        {'symbol': 'MA', 'name': '万事达', 'price': 380},
        
        # 零售行业
        {'symbol': 'WMT', 'name': '沃尔玛', 'price': 150},
        {'symbol': 'COST', 'name': '好市多', 'price': 550},
        {'symbol': 'TGT', 'name': '塔吉特', 'price': 170},
        
        # 能源行业
        {'symbol': 'XOM', 'name': '埃克森美孚', 'price': 100},
        {'symbol': 'CVX', 'name': '雪佛龙', 'price': 135},
        
        # 医疗行业
        {'symbol': 'JNJ', 'name': '强生', 'price': 160},
        {'symbol': 'PFE', 'name': '辉瑞', 'price': 33},
        {'symbol': 'UNH', 'name': '联合国健康', 'price': 480}
    ]
    
    print("=" * 70)
    print("         AI智能交易员 - 扩展训练版本")
    print("=" * 70)
    print("\n新增功能:")
    print("  ✅ 训练股票数量：10只 → 20只")
    print("  ✅ 交易策略：4种策略对比（双均线、动量、均值回归、RSI）")
    print("  ✅ 风险管理：止损2%、止盈5%、最大回撤15%")
    print("  ✅ 回测周期：1年 → 5年")
    print("  ✅ 性能指标：夏普比率、年化收益率")
    print()
    
    all_results = []
    
    for stock in stocks:
        try:
            result = train_stock_with_multiple_strategies(
                symbol=stock['symbol'],
                name=stock['name'],
                initial_price=stock['price']
            )
            all_results.append(result)
            print(f"\n⏸️  等待3秒后继续...")
            import time
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"训练 {stock['symbol']} 时出错: {e}")
            continue
    
    # 生成汇总报告
    generate_expanded_summary(all_results)
    
    return all_results


def generate_expanded_summary(results):
    """生成扩展版汇总报告"""
    print(f"\n{'='*70}")
    print("                    扩展训练汇总报告")
    print(f"{'='*70}\n")
    
    if not results:
        print("没有成功的训练结果")
        return
    
    # 计算每个股票的最佳策略
    stock_best_results = []
    for result in results:
        symbol = result['symbol']
        name = result['name']
        
        best_strategy = max(result['results'].items(), key=lambda x: x[1]['title'])
        strategy_name, strategy_result = best_strategy
        
        stock_best_results.append({
            'symbol': symbol,
            'name': name,
            'best_strategy': strategy_name,
            'return': strategy_result['title'],
            'annual_return': strategy_result['annual_return'],
            'trades': strategy_result['total_trades'],
            'sharpe': strategy_result['share_ratio']
        })
    
    # 按收益率排序
    sorted_stocks = sorted(stock_best_results, key=lambda x: x['return'], reverse=True)
    
    print(f"总训练股票数: {len(sorted_stocks)}")
    print()
    
    print(f"{'股票':<12} | {'名称':<12} | {'最佳策略':<10} | {'收益率':>10} | {'年化':>10} |评级")
    print("-" * 80)
    
    # 计算总体收益（假设每只股票投资$100,000）
    total_capital = len(sorted_stocks) * 100000
    total_final = sum(100000 * (1 + result['return']/100) for result in sorted_stocks)
    total_return = (total_final - total_capital) / total_capital * 100
    
    for r in sorted_stocks:
        ret = r['return']
        rating = "A" if ret > 20 else "B" if ret > 0 else "C"
        print(f"{r['symbol']:<12} | {r['name']:<12} | {r['best_strategy']:<10} | {ret:>9.2f}% | {r['annual_return']:>9.2f}% | {rating:>4}")
    
    print()
    print(f"投资组合统计:")
    print(f"  总投入资金: ${total_capital:,.2f}")
    print(f"  总最终价值: ${total_final:,.2f}")
    print(f"  总收益率: {total_return:.2f}%")
    print(f"  平均年化收益: {np.mean([r['annual_return'] for r in sorted_stocks]):.2f}%")
    
    # 策略统计
    print(f"\n策略应用统计:")
    strategy_counts = {}
    for result in all_results:
        best = max(result['results'].items(), key=lambda x: x[1]['title'])
        strategy_name = best[0]
        strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1
    
    for strategy, count in sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(all_results) * 100)
        print(f"  {strategy}: {count}/{len(all_results)} ({percentage:.0f}%)")
    
    # 保存汇总报告
    summary = {
        'total_stocks': len(sorted_stocks),
        'data_period_years': 5,
        'total_capital': total_capital,
        'total_final': total_final,
        'total_return': total_return,
        'average_annual_return': float(np.mean([r['annual_return'] for r in sorted_stocks])),
        'stock_results': stock_best_results,
        'strategy_counts': strategy_counts,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('training_summary_expanded.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ 汇总报告已保存: training_summary_expanded.json")
    
    return summary


if __name__ == '__main__':
    main()
