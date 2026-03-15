#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实股市行情数据训练AI交易员
"""

import json
import logging
from datetime import datetime, timedelta
from trader import AITrader
from data_fetcher import DataFetcher
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def train_multiple_stocks():
    """训练多个股票标的"""
    # 选择不同类型的股票进行训练
    stocks = [
        {'symbol': 'AAPL', 'name': '苹果', 'category': '科技'},
        {'symbol': 'MSFT', 'name': '微软', 'category': '科技'},
        {'symbol': 'GOOGL', 'name': '谷歌', 'category': '科技'},
        {'symbol': 'TSLA', 'name': '特斯拉', 'category': '汽车'},
        {'symbol': 'NVDA', 'name': '英伟达', 'category': '科技'},
        {'symbol': 'AMZN', 'name': '亚马逊', 'category': '电商'},
        {'symbol': 'META', 'name': 'Meta', 'category': '科技'},
        {'symbol': 'JPM', 'name': '摩根大通', 'category': '金融'},
        {'symbol': 'V', 'name': 'Visa', 'category': '金融'},
        {'symbol': 'WMT', 'name': '沃尔玛', 'category': '零售'}
    ]
    
    results = []
    
    print("=" * 70)
    print("         AI智能交易员 - 真实数据训练")
    print("=" * 70)
    
    for stock in stocks:
        print(f"\n{'='*70}")
        print(f"训练标的: {stock['name']} ({stock['symbol']})")
        print(f"{'='*70}")
        
        try:
            # 创建交易员
            trader = AITrader(
                symbol=stock['symbol'],
                strategy_type='ml',  # 使用机器学习策略
                config_path='config.json'
            )
            
            # 市场分析
            print(f"\n📊 正在分析 {stock['symbol']} ...")
            analysis = trader.analyze(period='2y')  # 分析2年数据
            
            if analysis:
                print(f"✅ 分析完成")
                print(f"   当前价格: ${analysis['current_price']:.2f}")
                print(f"   交易建议: {analysis['recommendation']}")
                print(f"   信号置信度: {analysis['final_signal']['confidence']:.2%}")
                print(f"   风险等级: {analysis['risk_assessment']['risk_level']}")
            
            # 回测
            print(f"\n📈 正在回测 {stock['symbol']} ...")
            end_date = datetime.now() - timedelta(days=1)
            start_date = datetime.now() - timedelta(days=365)
            
            backtest = trader.backtest(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                initial_capital=100000
            )
            
            if backtest:
                print(f"✅ 回测完成")
                print(f"   初始资金: ${backtest['initial_capital']:,.2f}")
                print(f"   最终价值: ${backtest['final_value']:,.2f}")
                print(f"   收益率: {backtest['total_return']:.2f}%")
                print(f"   交易次数: {backtest['total_trades']}")
            
            # 保存结果
            result = {
                'symbol': stock['symbol'],
                'name': stock['name'],
                'category': stock['category'],
                'analysis': analysis,
                'backtest': backtest,
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            
            # 保存单个结果
            filename = f"training_{stock['symbol']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"   结果已保存: {filename}")
            
        except Exception as e:
            logger.error(f"训练 {stock['symbol']} 时出错: {e}")
            continue
    
    # 生成汇总报告
    summary = generate_summary_report(results)
    
    return results, summary


def generate_summary_report(results):
    """生成汇总报告"""
    print(f"\n{'='*70}")
    print("                    训练汇总报告")
    print(f"{'='*70}\n")
    
    successful_results = [r for r in results if r['backtest']]
    
    if not successful_results:
        print("没有成功的训练结果")
        return None
    
    # 总体统计
    total_capital = sum(r['backtest']['initial_capital'] for r in successful_results)
    total_final = sum(r['backtest']['final_value'] for r in successful_results)
    total_return = (total_final - total_capital) / total_capital * 100
    
    print(f"训练股票数量: {len(successful_results)}")
    print(f"总投入资金: ${total_capital:,.2f}")
    print(f"总最终价值: ${total_final:,.2f}")
    print(f"总收益率: {total_return:.2f}%")
    print()
    
    # 各股票表现
    print(f"{'股票':<12} | {'名称':<12} | {'收益率':>10} | {'交易次数':>8} | {'评级':>6}")
    print("-" * 70)
    
    for r in successful_results:
        ret = r['backtest']['total_return']
        trades = r['backtest']['total_trades']
        
        if ret > 20:
            rating = "⭐⭐⭐⭐⭐"
        elif ret > 10:
            rating = "⭐⭐⭐⭐"
        elif ret > 0:
            rating = "⭐⭐⭐"
        elif ret > -10:
            rating = "⭐⭐"
        else:
            rating = "⭐"
        
        print(f"{r['symbol']:<12} | {r['name']:<12} | {ret:>9.2f}% | {trades:>8} | {rating:>6}")
    
    # 保存汇总报告
    summary = {
        'total_stocks': len(successful_results),
        'total_capital': total_capital,
        'total_final': total_final,
        'total_return': total_return,
        'results': successful_results,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('training_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 汇总报告已保存: training_summary.json")
    
    return summary


def main():
    """主函数"""
    try:
        print("🚀 开始使用真实股市数据训练AI交易员...\n")
        
        results, summary = train_multiple_stocks()
        
        print(f"\n{'='*70}")
        print("✅ 所有训练完成！")
        print(f"{'='*70}")
        print(f"\n生成的文件:")
        print(f"  - training_summary.json (汇总报告)")
        print(f"  - training_*.json (各股票训练结果)")
        print(f"\n项目文件位置: /ai_trader/")
        
    except Exception as e:
        logger.error(f"训练过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
