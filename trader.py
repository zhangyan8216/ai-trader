#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能交易员 - 主程序
支持多种交易策略和风险管理
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from data_fetcher import DataFetcher
from strategy import TradingStrategy
from risk_management import RiskManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AITrader:
    """AI智能交易员主类"""
    
    def __init__(self, symbol, strategy_type='ml', config_path='config.json'):
        """
        初始化交易员
        
        Args:
            symbol: 交易标的 (如 'AAPL', 'BTC-USD')
            strategy_type: 策略类型 ('ml', 'technical', 'hybrid')
            config_path: 配置文件路径
        """
        self.symbol = symbol
        self.strategy_type = strategy_type
        self.config = self.load_config(config_path)
        
        # 初始化组件
        self.data_fetcher = DataFetcher(symbol)
        self.strategy = TradingStrategy(strategy_type)
        self.risk_manager = RiskManager(self.config.get('risk', {}))
        
        logger.info(f"初始化AI交易员成功 - 标的: {symbol}, 策略: {strategy_type}")
    
    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 未找到，使用默认配置")
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            'risk': {
                'max_position_size': 0.1,  # 最大仓位比例
                'stop_loss': 0.02,  # 止损比例
                'take_profit': 0.05,  # 止盈比例
                'max_daily_loss': 0.05  # 最大日亏损
            },
            'trading': {
                'timeframe': '1d',
                'lookback_days': 252  # 回看天数
            }
        }
    
    def analyze(self, period='1y'):
        """
        分析市场数据并生成交易信号
        
        Args:
            period: 分析周期 (如 '1y', '6m', '3m')
        
        Returns:
            dict: 分析结果
        """
        logger.info(f"开始分析 {self.symbol} (周期: {period})")
        
        # 获取数据
        data = self.data_fetcher.fetch_data(period)
        if data is None or data.empty:
            logger.error("获取数据失败")
            return None
        
        # 技术分析
        technical_signals = self.strategy.technical_analysis(data)
        
        # 机器学习预测（如果是ML或混合策略）
        ml_signals = None
        if self.strategy_type in ['ml', 'hybrid']:
            ml_signals = self.strategy.ml_prediction(data)
        
        # 综合信号
        signal = self.strategy.generate_signal(technical_signals, ml_signals)
        
        # 风险评估
        risk_assessment = self.risk_manager.assess_risk(signal, data)
        
        # 生成报告
        report = {
            'symbol': self.symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': data['Close'].iloc[-1],
            'technical_signals': technical_signals,
            'ml_signals': ml_signals,
            'final_signal': signal,
            'risk_assessment': risk_assessment,
            'recommendation': self._get_recommendation(signal, risk_assessment)
        }
        
        logger.info(f"分析完成 - 信号: {signal['action']}, 置信度: {signal['confidence']:.2%}")
        
        return report
    
    def _get_recommendation(self, signal, risk_assessment):
        """生成交易建议"""
        action = signal['action']
        confidence = signal['confidence']
        risk_level = risk_assessment['risk_level']
        
        if action == 'buy':
            if confidence > 0.7 and risk_level == 'low':
                return '🟢 强烈建议买入'
            elif confidence > 0.5 and risk_level != 'high':
                return '🟡 谨慎买入'
            else:
                return '⚪ 观望'
        elif action == 'sell':
            if confidence > 0.7 and risk_level == 'low':
                return '🔴 强烈建议卖出'
            elif confidence > 0.5 and risk_level != 'high':
                return '🟠 考虑卖出'
            else:
                return '⚪ 观望'
        else:
            return '⚪ 持币观望'
    
    def backtest(self, start_date, end_date, initial_capital=100000):
        """
        回测策略
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            initial_capital: 初始资金
        
        Returns:
            dict: 回测结果
        """
        logger.info(f"开始回测 {start_date} 至 {end_date}")
        
        # 获取历史数据
        data = self.data_fetcher.fetch_historical(start_date, end_date)
        if data is None:
            logger.error("获取历史数据失败")
            return None
        
        # 模拟交易
        results = self._simulate_trading(data, initial_capital)
        
        return results
    
    def _simulate_trading(self, data, initial_capital):
        """模拟交易过程"""
        capital = initial_capital
        position = 0
        trades = []
        
        for i in range(len(data) - 1):
            # 获取当前数据窗口
            window_data = data.iloc[:i+1]
            
            # 生成信号
            signal = self.analyze_window(window_data)
            
            # 执行交易
            if signal['action'] == 'buy' and position == 0:
                # 买入
                shares = int(capital / window_data['Close'].iloc[-1])
                position = shares
                capital -= shares * window_data['Close'].iloc[-1]
                trades.append({
                    'date': window_data.index[-1],
                    'action': 'buy',
                    'price': window_data['Close'].iloc[-1],
                    'shares': shares
                })
            
            elif signal['action'] == 'sell' and position > 0:
                # 卖出
                capital += position * window_data['Close'].iloc[-1]
                trades.append({
                    'date': window_data.index[-1],
                    'action': 'sell',
                    'price': window_data['Close'].iloc[-1],
                    'shares': position
                })
                position = 0
        
        # 计算最终价值
        final_value = capital + position * data['Close'].iloc[-1]
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': len(trades),
            'trades': trades
        }
    
    def analyze_window(self, window_data):
        """分析数据窗口并生成信号"""
        technical_signals = self.strategy.technical_analysis(window_data)
        ml_signals = None
        
        if self.strategy_type in ['ml', 'hybrid']:
            ml_signals = self.strategy.ml_prediction(window_data)
        
        return self.strategy.generate_signal(technical_signals, ml_signals)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI智能交易员')
    parser.add_argument('--symbol', type=str, default='AAPL',
                      help='交易标的 (如 AAPL, BTC-USD)')
    parser.add_argument('--strategy', type=str, default='ml',
                      choices=['ml', 'technical', 'hybrid'],
                      help='交易策略类型')
    parser.add_argument('--action', type=str, default='analyze',
                      choices=['analyze', 'backtest'],
                      help='执行动作')
    parser.add_argument('--period', type=str, default='1y',
                      help='分析周期 (1y, 6m, 3m)')
    parser.add_argument('--config', type=str, default='config.json',
                      help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建交易员
    trader = AITrader(args.symbol, args.strategy, args.config)
    
    # 执行动作
    if args.action == 'analyze':
        report = trader.analyze(args.period)
        print("\n" + "="*50)
        print("AI交易员分析报告")
        print("="*50)
        print(f"标的: {report['symbol']}")
        print(f"当前价格: ${report['current_price']:.2f}")
        print(f"分析时间: {report['timestamp']}")
        print(f"\n交易建议: {report['recommendation']}")
        print(f"风险等级: {report['risk_assessment']['risk_level']}")
        print("="*50)
        
        # 保存报告
        with open('analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n报告已保存到: analysis_report.json")
    
    elif args.action == 'backtest':
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        results = trader.backtest(start_date, end_date)
        
        print("\n" + "="*50)
        print("回测结果")
        print("="*50)
        print(f"初始资金: ${results['initial_capital']:,.2f}")
        print(f"最终价值: ${results['final_value']:,.2f}")
        print(f"总收益率: {results['total_return']:.2f}%")
        print(f"交易次数: {results['total_trades']}")
        print("="*50)


if __name__ == '__main__':
    main()
