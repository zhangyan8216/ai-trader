#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易策略模块 - 支持技术分析、机器学习和混合策略
"""

import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TradingStrategy:
    """交易策略类"""
    
    def __init__(self, strategy_type='ml'):
        """
        初始化策略
        
        Args:
            strategy_type: 策略类型 ('ml', 'technical', 'hybrid')
        """
        self.strategy_type = strategy_type
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
        logger.info(f"初始化策略: {strategy_type}")
    
    def technical_analysis(self, data):
        """
        技术分析
        
        Args:
            data: 包含技术指标的数据
        
        Returns:
            dict: 技术分析信号
        """
        try:
            latest = data.iloc[-1]
            signals = {}
            
            # MA交叉信号
            if not pd.isna(latest['MA5']) and not pd.isna(latest['MA20']):
                if latest['MA5'] > latest['MA20']:
                    signals['ma_cross'] = 'bullish'
                else:
                    signals['ma_cross'] = 'bearish'
            
            # RSI信号
            if not pd.isna(latest['RSI']):
                if latest['RSI'] < 30:
                    signals['rsi'] = 'oversold'
                elif latest['RSI'] > 70:
                    signals['rsi'] = 'overbought'
                else:
                    signals['rsi'] = 'neutral'
            
            # MACD信号
            if not pd.isna(latest['MACD_Diff']):
                if latest['MACD_Diff'] > 0:
                    signals['macd'] = 'bullish'
                else:
                    signals['macd'] = 'bearish'
            
            # 布林线信号
            if not(pd.isna(latest['BB_Upper']) or pd.isna(latest['BB_Lower'])):
                if latest['Close'] > latest['BB_Upper']:
                    signals['bollinger'] = 'overbought'
                elif latest['Close'] < latest['BB_Lower']:
                    signals['bollinger'] = 'oversold'
                else:
                    signals['bollinger'] = 'neutral'
            
            # 价格趋势
            if len(data) >= 5:
                recent_trend = data['Close'].iloc[-5:].pct_change().sum()
                if recent_trend > 0.02:
                    signals['trend'] = 'strong_up'
                elif recent_trend > 0:
                    signals['trend'] = 'up'
                elif recent_trend > -0.02:
                    signals['trend'] = 'down'
                else:
                    signals['trend'] = 'strong_down'
            
            logger.info(f"技术分析完成: {len(signals)} 个信号")
            return signals
            
        except Exception as e:
            logger.error(f"技术分析时出错: {e}")
            return {}
    
    def ml_prediction(self, data):
        """
        机器学习预测
        
        Args:
            data: 历史数据
        
        Returns:
            dict: ML预测结果
        """
        try:
            # 准备特征数据
            features = self._prepare_features(data)
            
            if features is None or len(features) < 50:
                logger.warning("数据不足，无法进行ML预测")
                return None
            
            # 创建标签（未来价格趋势）
            labels = self._create_labels(data, period=5)
            
            # 如果模型未训练，先训练
            if not self.is_trained:
                self._train_model(features, labels)
            
            # 预测
            prediction = self.model.predict([features.iloc[-1]])[0]
            probability = self.model.predict_proba([features.iloc[-1]])[0]
            
            return {
                'prediction': prediction,
                'probability': float(max(probability)),
                'buy_prob': float(probability[1] if len(probability) > 1 else probability[0]),
                'sell_prob': float(probability[0] if len(probability) > 1 else 0)
            }
            
        except Exception as e:
            logger.error(f"ML预测时出错: {e}")
            return None
    
    def _prepare_features(self, data):
        """
        准备特征数据
        
        Args:
            data: OHLCV数据
        
        Returns:
            pd.DataFrame: 特征数据
        """
        try:
            # 计算技术指标
            data = data.copy()
            data['RSI'] = data['Close'].rolling(window=14).mean()
            data['MA5'] = data['Close'].rolling(window=5).mean()
            data['MA20'] = data['Close'].rolling(window=20).mean()
            
            # 价格特征
            data['Price_Change'] = data['Close'].pct_change()
            data['Volume_Change'] = data['Volume'].pct_change()
            
            # 波动率
            data['Volatility'] = data['Price_Change'].rolling(window=10).std()
            
            # 选择特征列
            feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume',
                          'Price_Change', 'Volume_Change', 'Volatility']
            
            # 移除NaN值
            features = data[feature_cols].dropna()
            
            if len(features) == 0:
                return None
            
            return features
            
        except Exception as e:
            logger.error(f"准备特征时出错: {e}")
            return None
    
    def _create_labels(self, data, period=5):
        """
        创建标签（未来价格趋势）
        
        Args:
            data: 价格数据
            period: 预测周期
        
        Returns:
            np.array: 标签数组 (1=上涨, 0=下跌)
        """
        try:
            future_return = data['Close'].pct_change(periods=period).shift(-period)
            labels = (future_return > 0).astype(int)
            labels = labels.dropna().values
            return labels
        except Exception as e:
            logger.error(f"创建标签时出错: {e}")
            return None
    
    def _train_model(self, features, labels):
        """
        训练机器学习模型
        
        Args:
            features: 特征数据
            labels: 标签数据
        """
        try:
            # 对齐数据长度
            min_length = min(len(features), len(labels))
            features = features.iloc[:min_length]
            labels = labels[:min_length]
            
            if len(features) < 30:
                logger.warning("数据不足，无法训练模型")
                return
            
            # 分割训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )
            
            # 训练模型
            self.model.fit(X_train, y_train)
            
            # 评估模型
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.is_trained = True
            logger.info(f"模型训练完成 - 准确率: {accuracy:.2%}")
            
        except Exception as e:
            logger.error(f"训练模型时出错: {e}")
    
    def generate_signal(self, technical_signals, ml_signals):
        """
        生成交易信号
        
        Args:
            technical_signals: 技术分析信号
            ml_signals: ML预测信号
        
        Returns:
            dict: 最终交易信号
        """
        buy_score = 0
        sell_score = 0
        total_signals = 0
        
        # 技术信号分析
        if technical_signals:
            if technical_signals.get('ma_cross') == 'bullish':
                buy_score += 2
            elif technical_signals.get('ma_cross') == 'bearish':
                sell_score += 2
            
            if technical_signals.get('rsi') == 'oversold':
                buy_score += 2
            elif technical_signals.get('rsi') == 'overbought':
                sell_score += 2
            
            if technical_signals.get('macd') == 'bullish':
                buy_score += 1
            elif technical_signals.get('macd') == 'bearish':
                sell_score += 1
            
            if technical_signals.get('bollinger') == 'oversold':
                buy_score += 1
            elif technical_signals.get('bollinger') == 'overbought':
                sell_score += 1
            
            if technical_signals.get('trend') in ['up', 'strong_up']:
                buy_score += 1
            elif technical_signals.get('trend') in ['down', 'strong_down']:
                sell_score += 1
            
            total_signals += len(technical_signals)
        
        # ML信号分析
        if ml_signals and self.is_trained:
            if self.strategy_type == 'ml':
                # 纯ML策略
                if ml_signals['prediction'] == 1:
                    buy_score += 3 * ml_signals['probability']
                else:
                    sell_score += 3 * ml_signals['probability']
            elif self.strategy_type == 'hybrid':
                # 混合策略
                if ml_signals['prediction'] == 1:
                    buy_score += 2 * ml_signals['probability']
                else:
                    sell_score += 2 * ml_signals['probability']
            
            total_signals += 1
        
        # 生成最终信号
        net_score = buy_score - sell_score
        confidence = min(abs(net_score) / max(total_signals, 1), 1.0)
        
        if net_score > 2:
            action = 'buy'
        elif net_score < -2:
            action = 'sell'
        else:
            action = 'hold'
        
        return {
            'action': action,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'strategy_type': self.strategy_type
        }
