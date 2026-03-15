#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI交易员使用示例
"""

from trader import AITrader
import json


def main():
    """示例程序"""
    
    print("AI智能交易员 - 示例程序")
    print("=" * 50)
    
    # 1. 创建交易员
    print("\n1. 创建交易员...")
    trader = AITrader(
        symbol='AAPL',  # 可以改为其他标的，如 'BTC-USD'
        strategy_type='ml',  # 可选: 'ml', 'technical', 'hybrid'
        config_path='config.json'
    )
    print("✅ 交易员创建成功")
    
    # 2. 分析市场
    print("\n2. 分析市场...")
    report = trader.analyze(period='6m')  # 分析最近6个月
    
    if report:
        print("\n" + "=" * 50)
        print("📊 分析报告")
        print("=" * 50)
        print(f"标的: {report['symbol']}")
        print(f"当前价格: ${report['current_price']:.2f}")
        print(f"交易建议: {report['recommendation']}")
        print(f"最终信号: {report['final_signal']['action']}")
        print(f"信号置信度: {report['final_signal']['confidence']:.2%}")
        print(f"风险等级: {report['risk_assessment']['risk_level']}")
        print("=" * 50)
        
        # 保存详细报告
        with open('analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n详细报告已保存到: analysis_report.json")
    else:
        print("❌ 分析失败")
    
    # 3. 回测
    print("\n3. 开始回测...")
    end_date = "2026-02-28"
    start_date = "2025-02-28"
    
    results = trader.backtest(start_date, end_date, initial_capital=100000)
    
    if results:
        print("\n" + "=" * 50)
        print("📈 回测结果")
        print("=" * 50)
        print(f"初始资金: ${results['initial_capital']:,.2f}")
        print(f"最终价值: ${results['final_value']:,.2f}")
        print(f"总收益率: {results['total_return']:.2f}%")
        print(f"交易次数: {results['total_trades']}")
        
        # 计算胜率
        buy_trades = [t for t in results['trades'] if t['action'] == 'buy']
        sell_trades = [t for t in results['trades'] if t['action'] == 'sell']
        
        if len(sell_trades) > 0:
            print(f"完整交易对数: {min(len(buy_trades), len(sell_trades))}")
        
        print("=" * 50)
    else:
        print("❌ 回测失败")


if __name__ == '__main__':
    try:
        main()
        print("\n✅ 程序执行完成")
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
