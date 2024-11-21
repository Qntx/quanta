

<h1 style="text-align: center; margin-bottom: 0.5rem;">
    <a href="https://github.com/Qntx/SigmaData" style="text-decoration: none; color: inherit;">
        Σ-Data
    </a>
</h1>
<p style="text-align: center; font-size: 1rem; color: #555; margin-top: 0;">
    <strong style="color: #007acc;">v0.4.0</strong>
</p>

**ΣData** 是一个高效的 Python 数据管理包，专为加密货币交易数据设计。它集成了 **CCXT** 库，支持从多个交易所获取历史 **ohlcv** 与 **trades** 数据，并通过本地 **SQLite** 数据库存储优化数据访问性能。无论是用于回测、分析，还是开发交易策略，**ΣData** 都能提供可靠的数据支持。

---

## 🌟 功能特性

- **异步环境支持**：提供异步接口，提升高并发环境下的数据获取效率。
- **多交易所支持**：集成 CCXT，支持 Binance、Bybit、Bitget 等主流交易所，覆盖多种资产类型。
- **历史数据检索**：快速获取并存储历史 OHLCV 数据与 Trades 数据，支持自动检测并补充缺失数据，确保数据完整性。
- **数据库存储**：使用本地 SQLite 数据库存储，减少重复 API 调用，提升数据访问速度，特别适合回测和分析场景。
- **可配置代理**：灵活支持 HTTP 和 WebSocket 代理配置，适应复杂的网络环境需求。

---

## 📦 环境配置

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

## 🛠️ 未来计划

- [ ] 优化时间周期：优化不同时间周期数据获取的准确性。
- [ ] 支持历史交易记录获取：通过实现 `TradeManager` 与 `Trade` 类实现。
- [ ] 支持实时数据流：集成 `ccxt.pro` 实时数据流订阅，实现与历史数据无缝衔接。
- [ ] 单元测试覆盖率提升：增加对核心模块的单元测试，提升代码质量和稳定性。
- [x] 异步版本：完整的异步功能支持。

---

## 📋 版本日志

### v0.4.0

- **项目重构**：重构了项目架构，解决了一分钟时间线下最新数据获取的不准确性。
- **异步支持**：添加了异步版本的功能支持。

### v0.3.0

- **项目重构**：重构了项目架构，优化了代码结构，减少了冗余代码，提高了项目的可维护性和可读性。
- **DataManager 类**：重新编写了 `DataManager` 类，底层基于 `pandas.DataFrame` 进行数据管理，用户可以通过传入 `columns=['date', 'timestamp', 'open', 'high', 'low', 'close', 'volume']` 来灵活选取所需数据。更新后的数据获取功能采用左闭右闭区间，确保传入的开始时间和终止时间内的数据都能获取。
- **Data 类**：新增了 `Data` 类，专为高性能数据管理设计，基于 `numpy` 实现，支持增量数据更新，并伴随着多线程回调函数的运行，提供更灵活且高效的数据处理方案。

### v0.2.0

- **日志管理**：更新了 基于`loguru` 的日志管理配置，并在项目中初步使用，提升了日志记录的效率和可读性。[SigmaLog](https://github.com/qntx/SigmaLog)
- **网络代理**：优化了网络代理模块，提高了网络请求的稳定性。
- **CcxtSource 类**：重写了 `CcxtSource` 类，优化了与交易所接口的对接，提升了数据获取的稳定性与性能。数据获取功能也改为左闭右闭，确保时间区间的准确性，替代了之前的左闭右开方案。
- **CCXT 版本更新**：更新了 `ccxt` 版本至 `v4.4.14`，确保兼容最新交易所接口与功能。

### v0.1.0

- 初始版本发布，支持基本的历史 OHLCV 数据获取与存储。
- 提供 SQLite 数据库集成，优化本地数据管理。
- 集成 CCXT 库，实现多交易所统一接口。

