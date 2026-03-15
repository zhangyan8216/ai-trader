#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险管理模块 - 控制交易风险
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskManager:
    """风险管理器"""
    
    def __init__(self, config):
        """
        初始化风险管理器
        
        Args:
            config: 风险管理配置字典
        """
        self.config = config
        self.daily_trades = []
        self.daily_pnl = 0
        self.max_daily_loss = config.get('max_daily_loss', 0.05)  # 5%
        
        logger.info("风险管理器初始化完成")
    
    def assess_risk(self, signal, data):
        """
        评估交易风险
        
        Args:
            signal: 交易信号
            data: 市场数据
        
        Returns:
            dict: 风险评估结果
        """
        risk_factors = []
        
        # 1. 波动率风险
        volatility = self._calculate_volatility(data)
        if volatility > 0.03:  # 3%以上波动率
            risk_factors.append('高波动率')
        
        # 2. 流动性风险
        liquidity = self._assess_liquidity(data)
        if liquidity == 'low':
            risk_factors.append('低流动性')
        
        # 3. 趋势风险
        trend_risk = self._trend_risk_assessment(data)
        if trend_risk:
            risk_factors.append(trend_risk)
        
        # 4. 信号置信度风险
        if signal['confidence'] < 0.5:
            risk_factors.append('低置信度')
        
        # 5. 日亏损风险
        if abs(self.daily_pnl) > self.max_daily_loss:
            risk_factors.append('超过日亏损限额')
        
        # 计算风险等级
        risk_level = self._calculate_risk_level(len(risk_factors))
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'volatility': volatility,
            'liquidity': liquidity,
            'can_trade': risk_level != 'high' and abs(self.daily_pnl) < self.max_daily_loss
        }
    
    def _calculate_volatility(self, data, window=20):
        """
        计算波动率
        
        Args:
            data: 价格数据
            window: 计算窗口
        
        Returns:
            float: 波动率
        """
        try:
            if len(data) < window:
                window = len(data) - 1
            
            returns = data['Close'].pct_change().dropna()
            volatility = returns.rolling(window=window).std().iloc[-1]
            return float(volatility)
        except:
            return 0.02  # 默认波动率
    
    def _assess_liquidity(self, data):
        """
        评估流动性
        
        Args:
            data: 市场数据
        
        Returns:
            str: 流动性等级 ('high', 'medium', 'low')
        """
        try:
            avg_volume = data['Volume'].tail(10).mean()
            
            if avg_volume > 1000000:
                return 'high'
            elif avg_volume > 100000:
                return 'medium'
            else:
                return 'low'
        except:
            return 'medium'
    
    def _trend_risk_assessment(self, data):
        """
        趋势风险评估
        
        Args:
            data: 价格数据
        
        Returns:
            str: 风险描述
        """
        try:
            if len(data) < 20:
                return None
            
            recent_price = data['Close'].iloc[-1]
            ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
            
            if recent_price < ma20 * 0.95:
                return '价格低于20日均线超5%'
            elif recent_price > ma20 * 1.05:
                return '价格高于20日均线超5%'
            
            return None
        except:
            return None
    
    def _calculate_risk_level(self, risk_factor_count):
        """
        计算风险等级
        
        Args:
            risk_factor_count: 风险因素数量
        
        Returns:
            str: 风险等级 ('low', 'medium', 'high')
        """
        if risk_factor_count == 0:
            return 'low'
        elif risk_factor_count <= 2:
            return 'medium'
        else:
            return 'high'
    
    def calculate_position_size(self, capital, signal, risk_assessment):
        """
        计算仓位大小
        
        Args:
            capital: 可用资金
            signal: 交易信号
            risk_assessment: 风险评估
        
        Returns:
            float: 建议仓位金额
        """
        max_position_ratio = self.config.get('max_position_size', 0.1)  # 默认10%
        
        # 根据风险等级调整仓位
        risk_multiplier = {
            'low': 1.0,
            'medium': 0.5,
            'high': 0.0
        }
        
        # 根据信号置信度调整仓位
        confidence_multiplier = signal.get('confidence', 0.5)
        
        # 计算仓位
        position_ratio = max_position_ratio * risk_multiplier.get(
            risk_assessment['risk_level'], 0.5
        ) * confidence_multiplier
        
        return capital * position_ratio
    
    def set_stop_loss(self, entry_price, position_size):
        """
        设置止损价格
        
        Args:
            entry_price: 入场价格
            position_size: 仓位大小
        
        Returns:
            float: 止损价格
        """
        stop_loss_ratio = self.config.get('stop_loss', 0.02)  # 默认2%
        return entry_price * (1 - stop_loss_ratio)
    
    def set_take_profit(self, entry_price, position_size):
        """
        设置止盈价格
        
        Args:
            entry_price: 入场价格
            position_size: 仓位大小
        
        Returns:
            float: 止盈价格
        """
        take_profit_ratio = self.config.get('take_profit', 0.05)  # 默认5%
        return entry_price * (1 + take_profit_ratio)
    
    def update_daily_pnl(self, realized_pnl):
        """
        更新每日损益
        
        Args:
            realized_pnl: 已实现损益
        """
        self.daily_pnl += realized_pnl
        logger.info(f"更新日损益: {self.daily_pnl:.2%}")
        
        # 检查是否超过限额
        if abs(self.daily_pnl) > self.max_daily_loss:
            logger.warning(f"超过日亏损限额: {abs(self.daily_pnl):.2%}")
    
    def reset_daily_stats(self):
        """重置每日统计"""
        self.daily_trades = []
        self.daily_pnl = 0
        logger.info("每日统计数据已重置")
    
    def generate_position_report(self, entry_price, current_price, position_size):
        """
        生成持仓报告
        
        Args:
            entry_price: 入场价格
            current_price: 当前价格
            position_size: 仓位大小
        
        Returns:
            dict: 持仓报告
        """
        pnl = (current_price - entry_price) * position_size
        pnl_ratio = (current_price - entry_price) / entry_price
        
        stop_loss = self.set_stop_loss(entry_price, position_size)
        take_profit = self.set_take_profit(entry_price, position_size)
        
        return {
            'entry_price': entry_price,
            'current_price': current_price,
            'position_size': position_size,
            'pnl': pnl,
            'pnl_ratio': pnl_ratio,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'distance_to_stop': (current_price - stop_loss) / entry_price,
            'distance_to_profit': (take_profit - current_price) / entry_price
        }
