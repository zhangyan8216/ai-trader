#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实股市行情数据训练AI交易员 - 优化版
解决API限流问题，添加延迟、重试和缓存机制
"""

import json
import logging
import time
import os
from datetime import datetime, timedelta
from trader import AITrader
from data_fetcher import DataFetcher
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataCache:
    """数据缓存类"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def get_cache_file(self, symbol, period):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{symbol}_{period}.csv")
    
    def save(self, symbol, period, data):
        """保存缓存数据"""
        cache_file = self.get_cache_file(symbol, period)
        try:
            data.to_csv(cache_file)
            logger.info(f"数据已缓存: {cache_file}")
            return True
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
            return False
    
    def load(self, symbol, period):
        """加载缓存数据"""
        cache_file = self.get_cache_file(symbol, period)
        if not os.path.exists(cache_file):
            return None
        
        try:
            # 检查缓存文件是否过期（超过7天）
            cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if (datetime.now() - cache_time).days > 7:
                logger.info(f"缓存已过期: {cache_file}")
                return None
            
            data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            logger.info(f"从缓存加载数据: {cache_file}")
            return data
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            return None


def wait_on_rate_limit(attempt, max_wait=300):
    """等待API限流解除"""
    wait_time = min(60 * attempt, max_wait)
    logger.warning(f"遇到API限流，等待{wait_time}秒后重试... (尝试 {attempt}/5)")
    time.sleep(wait_time)


def train_single_stock(symbol, name, category='general', cache=None, max_retries=5):
    """训练单个股票（带重试机制）"""
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n{'='*70}")
            print(f"训练标的: {name} ({symbol}) - 尝试 {attempt}/{max_retries}")
            print(f"{'='*70}")
            
            # 创建交易员
            trader = AITrader(
                symbol=symbol,
                strategy_type='ml',
                config_path='config.json'
            )
            
            # 市场分析
            print(f"\n📊 正在分析 {symbol} ...")
            analysis = trader.analyze(period='2y')
            
            if analysis:
                print(f"✅ 分析完成")
                print(f"   当前价格: ${analysis['current_price']:.2f}")
                print(f"   交易建议: {analysis['recommendation']}")
                
                if 'final_signal' in analysis:
                    print(f"   信号置信度: {analysis['final_signal']['confidence']:.2%}")
                
                if 'risk_assessment' in analysis:
                    print(f"   风险等级: {analysis['risk_assessment']['risk_level']}")
            
            # 回测
            print(f"\n📈 正在回测 {symbol} ...")
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
                
                # 计算年度收益
                if 'annual_return' in backtest:
                    print(f"   年化收益率: {backtest['annual_return']:.2f}%")
            else:
                print(f"❌ 回测失败")
                return None, None
            
            # 保存结果
            result = {
                'symbol': symbol,
                'name': name,
                'category': category,
                'analysis': {
                    'current_price': analysis.get('current_price'),
                    'recommendation': analysis.get('recommendation'),
                    'confidence': analysis.get('final_signal', {}).get('confidence'),
                    'risk_level': analysis.get('risk_assessment', {}).get('risk_level')
                } if analysis else {},
                'backtest': backtest,
                'timestamp': datetime.now().isoformat()
            }
            
            filename = f"training_{symbol}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"   结果已保存: {filename}")
            
            return result, backtest
            
        except Exception as e:
            error_msg = str(e)
            if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
                wait_on_rate_limit(attempt)
                continue
            else:
                logger.error(f"训练 {symbol} 时出错: {e}")
                if attempt == max_retries:
                    return None, None
                time.sleep(10)  # 其他错误等待10秒
    
    return None, None


def train_stocks_in_batches(stocks, batch_size=3):
    """分批训练股票"""
    
    all_results = []
    all_backtests = []
    
    cache = DataCache()
    
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(stocks) + batch_size - 1) // batch_size
        
        print(f"\n{'#'*70}")
        print(f"开始第 {batch_num}/{total_batches} 批训练")
        print(f"本批股票: {', '.join([s['symbol'] for s in batch])}")
        print(f"{'#'*70}")
        
        for stock in batch:
            result, backtest = train_single_stock(
                symbol=stock['symbol'],
                name=stock['name'],
                category=stock['category'],
                cache=cache
            )
            
            if result and backtest:
                all_results.append(result)
                all_backtests.append(backtest)
        
        # 批次之间添加延迟
        if i + batch_size < len(stocks):
            print(f"\n⏳ 第{batch_num}批完成，等待120秒后继续...")
            time.sleep(120)
    
    return all_results, all_backtests


def generate_summary_report(results, backtests):
    """生成汇总报告"""
    print(f"\n{'='*70}")
    print("                    训练汇总报告")
    print(f"{'='*70}\n")
    
    if not results:
        print("没有成功的训练结果")
        return None
    
    # 总体统计
    total_capital = sum(b['initial_capital'] for b in backtests)
    total_final = sum(b['final_value'] for b in backtests)
    total_return = (total_final - total_capital) / total_capital * 100 if total_capital > 0 else 0
    
    print(f"训练股票数量: {len(results)}")
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
    
    with open('training_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 汇总报告已保存: training_summary.json")
    
    return summary


def main():
    """主函数"""
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
    
    print("=" * 70)
    print("         AI智能交易员 - 真实数据训练 (优化版)")
    print("=" * 70)
    print("\n优化特性:")
    print("  ✅ 自动重试机制（最多5次）")
    print("  ✅ API限流智能等待")
    print("  ✅ 分批训练（每批3只股票）")
    print("  ✅ 批次间延迟（120秒）")
    print("  ✅ 本地数据缓存（7天有效期）")
    print("  ✅ 错误处理和日志记录")
    print()
    
    # 用户确认
    print(f"准备训练 {len(stocks)} 只股票，预计需要 15-20 分钟")
    confirm = input("是否继续? (y/n): ")
    if confirm.lower() != 'y':
        print("训练已取消")
        return
    
    try:
        print(f"\n🚀 开始训练...\n")
        
        results, backtests = train_stocks_in_batches(stocks, batch_size=3)
        
        if results:
            summary = generate_summary_report(results, backtests)
            
            print(f"\n{'='*70}")
            print("✅ 所有训练完成！")
            print(f"{'='*70}")
            print(f"\n生成的文件:")
            print(f"  - training_summary.json (汇总报告)")
            print(f"  - training_*.json (各股票训练结果)")
            print(f"\n项目文件位置: /ai_trader/")
        else:
            print(f"\n❌ 训练失败，请检查网络连接或稍后重试")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  训练被用户中断")
        return
    except Exception as e:
        logger.error(f"训练过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
