# ΣData

**ΣData** 是一个高效的 Python 数据管理包，专为加密货币交易数据设计。它集成了 **CCXT** 库，支持从多个交易所获取历史 **ohlcv** 与 **trades** 数据，并通过本地 **SQLite** 数据库存储优化数据访问性能。无论是用于回测、分析，还是开发交易策略，**ΣData** 都能提供可靠的数据支持。

---

## 🌟 功能特性

- **异步环境支持**：提供异步接口，提升高并发环境下的数据获取效率。
- **多交易所支持**：集成 CCXT，支持 Binance、Bybit、Bitget 等主流交易所，覆盖多种资产类型。
- **历史数据检索**：快速获取并存储历史 OHLCV 数据，支持自动检测并补充缺失数据，确保数据完整性。
- **数据库存储**：使用本地 SQLite 数据库存储，减少重复 API 调用，提升数据访问速度，特别适合回测和分析场景。
- **可配置代理**：灵活支持 HTTP 和 WebSocket 代理配置，适应复杂的网络环境需求。

---

## 📦 安装

### 快速安装

使用以下命令直接安装：

```bash
pip install git+https://github.com/qntx/SigmaData.git
```

### 本地安装

如需进行本地开发和测试，克隆项目仓库并安装依赖项：

```
git clone https://github.com/qntx/SigmaData.git
cd SigmaData
pip install -r requirements.txt
```

---
