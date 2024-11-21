# 📘 使用指南 

欢迎来到 **ΣData** 使用指南！本指南将详细介绍 **ΣData** 的核心功能，包括如何高效获取 **OHLCV 数据** 和 **交易数据（Trades）**，以及同步与异步的使用方式。

------

## 🌟 功能概览 

**ΣData** 提供以下核心功能，助您轻松管理和检索交易数据：

- 📊 **获取数据**：支持获取历史和实时的 **OHLCV 数据** 和 **历史交易数据（Trades）**。
- 🗂️ **管理数据**：通过基于 Numpy 的高效存储和检索优化，提高数据访问速度。
- ⚡ **异步支持**：灵活适配高性能与高并发场景，同时提供同步和异步处理能力。

!!! note "适用场景"
	 **ΣData** 适用于量化回测、实时交易和市场分析等场景。

------

## 📈 获取数据 

### 1. 获取 OHLCV 数据

#### 1.1 同步方式 🔗

📦 **核心组件**：`DataManager`

- 描述：通过 `DataManager` 获取多周期、多品种的历史和实时 OHLCV 数据。

📋 **参数说明**：

- **`symbol`**：交易对名称（如 `BTC/USDT`）。
- **`timeframe`**：时间周期（如 `1m`, `1h`）。
- **`start_date`**：数据开始时间。
- **`end_date`**：数据结束时间。
- **`columns`**：需要返回的字段列表（如 `open`, `close`）。

📦 **功能描述**

- 高效获取多周期多品种的历史 OHLCV 数据。
- 自动处理时间范围与数据缺失补全。

🛠️ **适用场景**

- 数据初始化
- 静态回测环境

??? example "获取 OHLCV 数据示例" 

    ```python 
    
    from sigmadata import DataManager
    from sigmalog import LoguruConfig # 不是必须的
    
    LoguruConfig.load("./configs/log_config.json")
    
    param = {
        "httpsProxy": "http://127.0.0.1:7890",
        "wsProxy": "http://127.0.0.1:7890",
    }


    def main():
        exchange = "bitget"
        symbol = "BTC/USDT:USDT"
        timeframe = "15m"
        start_date = "2023-10-06T16:00:00.00Z"
        end_date = "2024-11-07T12:05:00.00Z"
        # end_date = None
    
        df = DataManager(exchange, param, db_path="./db/crypto_data.db").get_data(
            symbol,
            timeframe,
            start_date,
            end_date,
            price_type="default",
            limit=200,
            columns=["date", "open", "high", "low", "close", "volume"],
        )
    
        print(df)
        df.to_csv(f"btc_usdt_{timeframe}_data.csv", index=False)


    if __name__ == "__main__":
        main()
    
    ```

#### 1.2 异步方式 ⚡

📦 **核心组件**：异步 `DataManager`

- 描述：适合高频交易和实时数据监控场景，避免阻塞主线程。

??? example "异步获取 OHLCV 数据" 

    ```python 
    
    import asyncio
    import sys
    import ccxt.async_support as ccxt
    from sigmadata.async_support.data_manager import DataManager
    from sigmalog import LoguruConfig
    
    LoguruConfig.load("./configs/log_config.json")
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    param = {
        "httpsProxy": "http://127.0.0.1:7890",
        "wsProxy": "http://127.0.0.1:7890",
    }


    async def main():
        exchange = ccxt.bitget(param)
        symbol = "BTC/USDT:USDT"
        timeframe = "1m"
        start_date = "2024-10-06T16:00:00.00Z"
        end_date = "2024-11-07T12:05:00.00Z"
        # end_date = None
    
        dm = DataManager(
            exchange_name="bitget", exchange=exchange, db_path="./db/crypto_data.db"
        )
        await dm.open()
    
        df = await dm.get_data(
            symbol,
            timeframe,
            start_date,
            end_date,
            limit=200,
            columns=["date", "open", "high", "low", "close", "volume"],
        )
    
        print(df)
    
        await dm.close()


    if __name__ == "__main__":
        asyncio.run(main())
    
    ```

### 2. 获取 Trades 数据（开发中）

## 🗂️ 数据管理

### 1. 管理 OHLCV 数据

📦 **核心组件**：`Data`

- 描述：本地存储和检索 OHLCV 数据，支持自动缓存。

📋 **功能说明**：

- 存储数据到 SQLite 数据库。
- 提供高效的数据查询。

------

### 2. 管理 Trades 数据（开发中）

📦 **核心组件**：`Trade`

- 描述：存储和管理市场历史交易记录。

📋 **功能说明**：

- 支持按时间过滤和聚合交易数据。
- 提供快速查询接口，适合高频场景。

