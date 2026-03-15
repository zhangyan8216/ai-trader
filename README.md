# 🎯 AI智能交易员

**基于机器学习的股市模拟训练系统 - 21.83%总收益率**

---

## 🎉 项目概述

AI智能交易员是一个基于机器学习和技术分析的交易系统，支持多种交易策略和风险管理模块。通过模拟和回测验证策略有效性，为实际交易提供决策支持。

---

## 📊 最新成果

**模拟训练结果（2026-03-15）：**
- 训练股票：10只
- 初始资金：$1,000,000
- 最终价值：$1,218,250.51
- **总收益率：21.83%**
- 年化收益率：7.2%

### 收益率排行榜

| 排名 | 股票 | 名称 | 收益率 | 评级 |
|------|------|------|--------|------|
| 🥇 | JPM | 摩根大通 | 161.94% | ⭐⭐⭐⭐⭐ |
| 🥈 | META | Meta | 30.06% | ⭐⭐⭐⭐⭐ |
| 🥉 | NVDA | 英伟达 | 27.66% | ⭐⭐⭐⭐ |
| 4 | TSLA | 特斯拉 | 16.59% | ⭐⭐⭐⭐ |
| 5 | V | Visa | 7.17% | ⭐⭐⭐ |

---

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行模拟训练
```bash
python train_demo.py
```

### 运行真实数据训练
```bash
python train_with_real_data.py
```

### 查看示例
```bash
python example.py
```

---

## 📁 项目结构

```
ai-trader/
├── trader.py                        # 主程序
├── strategy.py                      # 交易策略模块
├── risk_management.py               # 风险管理模块
├── data_fetcher.py                  # 数据获取模块
├── train_demo.py                     # 模拟训练演示
├── train_with_real_data.py           # 真实数据训练
├── train_with_real_data_optimized.py # 优化版真实数据训练
├── train_with_simulated_data.py      # 模拟数据训练
├── visualizer.py                     # 数据可视化
├── example.py                        # 使用示例
├── config.json                       # 配置文件
├── requirements.txt                  # 依赖包
├── README.md                         # 项目说明
├── USER_GUIDE.md                     # 用户指南
└── training_results/                 # 训练结果
    ├── training_summary_demo.json    # 汇总报告
    └── training_*.json                # 各股票结果
```

---

## 🎮 核心功能

### 1. 交易策略系统
- **机器学习策略** - 基于历史数据的预测模型
- **技术分析策略** - MA、RSI、MACD、布林带等
- **混合策略** - ML + 技术分析结合

### 2. 风险管理
- 最大仓位限制：10%
- 止损比例：2%
- 止盈比例：5%
- 最大日亏损：5%

### 3. 数据获取
- 支持多股票数据
- 实和历史数据
- 数据清洗和预处理

### 4. 回测系统
- 历史回测
- 性能指标计算
- 策略对比分析

### 5. 可视化
- 价格走势图
- 技术指标图表
- 交易信号展示
- 回测结果可视化

---

## 🛠️ 技术栈

- **数据处理**: Pandas, NumPy
- **机器学习**: Scikit-learn
- **技术分析**: TA-Lib
- **数据源**: yfinance
- **可视化**: Matplotlib, Plotly
- **日志**: Python logging

---

## ⚙️ 配置说明

### 交易配置 (config.json)
```json
{
  "risk": {
    "max_position_size": 0.1,    // 最大仓位10%
    "stop_loss": 0.02,             // 止损2%
    "take_profit": 0.05,           // 止盈5%
    "max_daily_loss": 0.05         // 最大日亏损5%
  },
  "trading": {
    "timeframe": "1d",             // 时间周期
    "lookback_days": 252           // 回溯天数
  },
  "strategy": {
    "default": "ml",               // 默认策略
    "ml": {
      "model_type": "RandomForest",
      "n_estimators": 100,
      "prediction_period": 5        // 预测周期（天）
    }
  }
}
```

---

## 📈 支持的技术指标

- **移动平均线** - MA5, MA10, MA20, MA50
- **相对强弱指标** - RSI
- **MACD** - 指数平滑异同移动平均线
- **布林带** - BB
- **波动率指标** - ATR, 历史波动率
- **成交量指标** - OBV, 成交量移动平均

---

## 📚 文档

- [项目说明](README.md)
- [用户指南](USER_GUIDE.md)
- [训练结果](training_results/training_summary_demo.json)

---

## ⚠️ 重要提示

1. **学习目的** - 本系统仅供学习和研究使用
2. **风险提示** - 实际交易需谨慎，不保证盈利
3. **数据免责** - 使用的外部数据源可能存在准确性问题
4. **模型限制** - 基于历史数据，未来表现可能不同

---

## 🎯 性能指标

### 系统性能
- 训练速度：~5秒/股票（模拟数据）
- 回测速度：~2秒/股票
- 内存占用：<100MB
- 支持股票数量：无限制

### 交易指标
- 年化收益率：7.2%
- 夏普比率：计算中
- 最大回撤：待统计
- 胜率：统计中

---

## 🚀 使用示例

### 示例1：查看README
```bash
cat README.md
```

### 示例2：运行快速演示
```bash
python train_demo.py
```

### 示例3：查看训练结果
```bash
python -c "import json; print(json.dumps(json.load(open('training_summary_demo.json')), indent=2))"
```

---

## 💡 未来规划

### 功能增强
- [ ] 集成真实实时数据
- [ ] 添加自动交易功能
- [ ] 实现更多交易策略
- [ ] 支持加密货币

### 性能优化
- [ ] 模型训练优化
- [ ] 回测速度优化
- [ ] 内存使用优化

### 风险管理
- [ ] 投资组合优化
- [ ] 相关性分析
- [ ] 对冲策略实现

---

## 🤝 贡献

欢迎提交Issues和Pull Requests！

---

## 📞 支持

- 查看文档或提交Issues
- 答疑：功能介绍、使用说明

---

## 📦 许可证

MIT License

---

**🎉 AI智能交易员 - 总收益率21.83%，年化收益率7.2%！**
