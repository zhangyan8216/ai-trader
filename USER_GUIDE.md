# AI智能交易员 - 使用指南

## 目录
1. [快速开始](#快速开始)
2. [功能说明](#功能说明)
3. [配置详解](#配置详解)
4. [策略说明](#策略说明)
5. [风险管理](#风险管理)
6. [常见问题](#常见问题)

## 快速开始

### 1. 安装依赖

```bash
cd ai_trader
pip install -r requirements.txt
```

注意：TA-Lib 需要单独安装
- Linux: `sudo apt-get install ta-lib`
- MacOS: `brew install ta-lib`
- Windows: 下载编译版本

### 2. 基本使用

```bash
# 运行示例程序
python example.py

# 或者直接使用主程序
python trader.py --symbol AAPL --strategy ml
```

### 3. 查看分析结果

程序运行后会生成：
- `analysis_report.json` - 详细分析报告
- `trading.log` - 交易日志
- 各种图表文件

## 功能说明

### 市场分析

实时分析市场数据，生成交易信号：

```python
from trader import AITrader

trader = AITrader(symbol='AAPL', strategy_type='ml')
report = trader.analyze(period='6m')
```

### 策略回测

测试策略历史表现：

```python
results = trader.backtest(
    start_date='2025-01-01',
    end_date='2025-12-31',
    initial_capital=100000
)
```

### 数据可视化

生成精美的分析图表：

```python
from visualizer import TradingVisualizer
from data_fetcher import DataFetcher

fetcher = DataFetcher('AAPL')
data = fetcher.fetch_data('6m')

viz = TradingVisualizer()
viz.plot_price_with_indicators(data, 'AAPL')
```

## 配置详解

### 风险管理配置

在 `config.json` 中配置：

```json
{
  "risk": {
    "max_position_size": 0.1,    // 单笔最大仓位比例 (10%)
    "stop_loss": 0.02,           // 止损百分比 (2%)
    "take_profit": 0.05,         // 止盈百分比 (5%)
    "max_daily_loss": 0.05       // 最大日亏损 (5%)
  }
}
```

### 交易配置

```json
{
  "trading": {
    "timeframe": "1d",          // 分析周期 (1d, 1h, 15m...)
    "lookback_days": 252        // 历史数据天数
  }
}
```

## 策略说明

### 1. 技术分析策略 (technical)

基于经典技术指标：
- 移动平均线 (MA5, MA20, MA50)
- 相对强度指标 (RSI)
- MACD
- 布林线

选择方式：
```bash
python trader.py --symbol AAPL --strategy technical
```

### 2. 机器学习策略 (ml)

使用随机森林算法进行预测：
- 基于历史价格数据
- 自动学习市场模式
- 动态调整预测权重

选择方式：
```bash
python trader.py --symbol AAPL --strategy ml
```

### 3. 混合策略 (hybrid)

结合技术分析和机器学习：
- 技术分析提供基础信号
- ML模型进行确认和增强
- 提高信号可靠性

选择方式：
```bash
python trader.py --symbol AAPL --strategy hybrid
```

## 风险管理

### 风险评估指标

- **波动率风险**: 市场价格波动程度
- **流动性风险**: 交易量是否充足
- **趋势风险**: 价格趋势是否健康
- **置信度风险**: 信号强度

### 仓位计算

根据风险等级动态调整仓位：
- 低风险: 满仓 (默认10%)
- 中风险: 半仓
- 高风险: 不建仓

### 止损止盈

- 止损: 默认 -2%
- 止盈: 默认 +5%
- 可在配置文件中调整

## 常见问题

### Q1: 可以交易哪些标的？

A: 支持任何yfinance支持的标的：
- 美股: AAPL, TSLA, GOOGL 等
- 加密货币: BTC-USD, ETH-USD 等
- 指数: ^GSPC (^SPX), ^DJI 等

### Q2: 数据从哪里获取？

A: 使用Yahoo Finance免费数据源，无需API密钥。

### Q3: 准确率如何？

A: 历史回测中通常能达到50-70%的准确率，但：
- 过去表现不代表未来
- 建议先在模拟环境测试
- 始终使用止损保护

### Q4: 可以实时交易吗？

A: 当前版本仅提供分析和建议，不支持实际交易。
⚠️ 建议用于辅助决策，不盲目跟随。

### Q5: 如何提高准确率？

A: 尝试以下方法：
1. 使用混合策略 (hybrid)
2. 增加历史数据量
3. 调整风险管理参数
4. 多标的组合分析

### Q6: 遇到报错怎么办？

A: 常见问题：
- `ModuleNotFoundError`: 安装依赖
- `Data Not Found`: 检查标的代码
- `TA-Lib error`: 单独安装TA-Lib

## 高级功能

### 自定义策略

继承 `TradingStrategy` 类：

```python
from strategy import TradingStrategy

class MyStrategy(TradingStrategy):
    def generate_signal(self, technical_signals, ml_signals):
        # 自定义信号逻辑
        pass
```

### 实时监控

结合定时任务定期分析：

```bash
# 使用 cron 每小时运行一次
0 * * * * cd /path/to/ai_trader && python trader.py --symbol AAPL
```

## 注意事项

⚠️ **重要提示**

1. **仅供学习参考** - 不构成投资建议
2. **风险自担** - 实际交易需谨慎
3. **先模拟后实盘** - 建议充分测试
4. **持续优化** - 市场在变化，策略需调整
5. **资金管理** - 不要投入超过承受能力的资金

## 技术支持

如有问题或建议，欢迎反馈！

---

**免责声明**: 本软件仅供教育和研究目的使用。作者不对使用本软件造成的任何损失负责。投资有风险，入市需谨慎。
