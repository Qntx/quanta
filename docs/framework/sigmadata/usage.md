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

#### **核心组件**：`DataManager`

- 描述：通过 `DataManager` 获取多周期、多品种的历史和实时 OHLCV 数据。

!!! note "适用场景"
- 数据初始化
- 静态回测环境

**功能说明**

- 高效获取多周期多品种的历史 OHLCV 数据。
- 自动处理时间范围与数据缺失补全。

##### 核心方法：`get_data`

```python
def get_data(
    self,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: Optional[str] = None,
    price_type: str = "default",
    limit: int = 200,
    columns: Optional[List[str]] = None,
) -> pd.DataFrame
```

**参数说明**

| 参数         | 类型                     | 描述                                                         |
| ------------ | ------------------------ | ------------------------------------------------------------ |
| `symbol`     | `str`                    | 交易对名称，例如 `BTC/USDT:USDT`。                           |
| `timeframe`  | `str`                    | 时间周期（`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d`, `3d`, `1w`, `1M`） |
| `start_date` | `str`                    | 开始时间，ISO8601 格式。                                     |
| `end_date`   | `str`（可选）            | 结束时间，ISO8601 格式，默认为当前时间。                     |
| `price_type` | `str`（默认：`default`） | 数据类型（例如 `default` 或交易所特定的数据类型，如 `mark` 或 `index`）。 |
| `limit`      | `int`（默认：200）       | 每次 API 调用最大获取的数据条数。                            |
| `columns`    | `list[str]`（可选）      | 返回的数据列（ `['timestamp', 'date', 'open', 'high', 'low', 'close', 'volume']`）。 |

!!! warning
    1. limit 的具体数值因不同交易所而不同，API 限制填写错误会导致数据获取不全，下面是几个交易所的数据： 
        - OKX 默认为 100。 
        - Binance 默认为 1000。 
        - Bitget 默认为 200。 
        2. columns 中必须包含 `timestamp` 或 `date` 其中一个，否则获取的数据没有顺序。如果两个都没有填写，默认返回 `date`。



**示例代码**

??? example "获取 OHLCV 数据示例" 
	=== "同步获取方式"

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
    === "异步获取方式"
    	
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

---

## 🗂️ 数据管理

---

### 1. 管理 OHLCV 数据



**使用示例**

??? example "数据管理示例" 

    1.初始化数据
    
    ```python
    from sigmadata import Data
    
    data_instance = Data(capacity=1000)
    
    # 初始化数据
    initial_data = [
        [20230101, 100.0, 105.0, 99.0, 103.0, 1000],
        [20230102, 104.0, 107.0, 102.0, 106.0, 1500],
    ]
    data_instance.init(initial_data)
    
    # 查看数据
    print(data_instance.df)
    ```
    
    2.添加数据
    
    ```python
    # 添加单条数据
    new_point = [20230103, 106.0, 109.0, 104.0, 108.0, 1200]
    data_instance.add(new_point)
    
    # 添加多条数据
    new_data = [
        [20230104, 108.0, 111.0, 107.0, 110.0, 1300],
        [20230105, 110.0, 115.0, 109.0, 114.0, 1400],
    ]
    data_instance.add(new_data)
    
    print(data_instance.df)
    ```
    
    3.更新数据
    
    ```python
    # 更新最新数据
    updated_point = [20230105, 110.0, 116.0, 109.0, 115.0, 1450]
    data_instance.update(updated_point)
    
    print(data_instance.df)
    ```
    
    4.删除数据
    
    ```python
    # 删除最新数据
    data_instance.remove()
    
    # 清空所有数据
    data_instance.clear()
    
    print(data_instance.df)
    ```

------

### 2. 管理 Trades 数据（开发中）

