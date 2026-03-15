#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取模块 - 从多个数据源获取市场数据
"""

import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataFetcher:
    """数据获取器"""
    
    def __init__(self, symbol):
        """
        初始化数据获取器
        
        Args:
            symbol: 交易标的 (如 'AAPL', 'BTC-USD')
        """
        self.symbol = symbol
        logger.info(f"初始化数据获取器 - 标的: {symbol}")
    
    def fetch_data(self, period='1y'):
        """
        获取历史数据
        
        Args:
            period: 时间周期 (如 '1y', '6m', '3m', '1mo')
        
        Returns:
            pd.DataFrame: 包含OHLCV数据的DataFrame
        """
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                logger.error(f"获取数据失败: {self.symbol}")
                return None
            
            logger.info(f"成功获取 {len(data)} 条数据")
            return data
            
        except Exception as e:
            logger.error(f"获取数据时出错: {e}")
            return None
    
    def fetch_historical(self, start_date, end_date):
        """
        获取指定日期范围的历史数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: 包含OHLCV数据的DataFrame
        """
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.error(f"获取历史数据失败: {self.symbol}")
                return None
            
            logger.info(f"成功获取 {len(data)} 条历史数据")
            return data
            
        except Exception as e:
            logger.error(f"获取历史数据时出错: {e}")
            return None
    
    def get_realtime_quote(self):
        """
        获取实时报价
        
        Returns:
            dict: 包含实时价格信息的字典
        """
        try:
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            return {
                'symbol': self.symbol,
                'price': info.get('currentPrice'),
                'change': info.get('previousClose', 0) - info.get('currentPrice', 0) or 0,
                'change_percent': (info.get('currentPrice', 0) - info.get('previousClose', 0)) / info.get('previousClose', 1) * 100 if info.get('previousClose') else 0,
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'high_52w': info.get('fiftyTwoWeekHigh'),
                'low_52w': info.get('fiftyTwoWeekLow'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取实时报价时出错: {e}")
            return None
    
    def add_technical_indicators(self, data):
        """
        添加技术指标
        
        Args:
            data: 原始OHLCV数据
        
        Returns:
            pd.DataFrame: 添加技术指标后的数据
        """
        try:
            # 移动平均线
            data['MA5'] = data['Close'].rolling(window=5).mean()
            data['MA10'] = data['Close'].rolling(window=10).mean()
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['MA50'] = data['Close'].rolling(window=50).mean()
            
            # 成交量移动平均
            data['Volume_MA10'] = data['Volume'].rolling(window=10).mean()
            
            # 价格变化
            data['Price_Change'] = data['Close'].pct_change()
            
            # RSI (相对强度指标)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            data['MACD'] = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            data['MACD_Diff'] = data['MACD'] - data['MACD_Signal']
            
            # 布林线
            data['BB_Middle'] = data['Close'].rolling(window=20).mean()
            data['BB_Std'] = data['Close'].rolling(window=20).std()
            data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2)
            data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2)
            
            logger.info("技术指标计算完成")
            return data
            
        except Exception as e:
            logger.error(f"计算技术指标时出错: {e}")
            return data
