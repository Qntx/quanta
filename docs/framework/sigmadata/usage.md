# 使用指南 

欢迎来到 **ΣData** 使用指南！本指南将详细介绍 **ΣData** 的核心功能，包括如何高效获取 **OHLCV 数据** 和 **交易数据（Trades）**，以及同步与异步的使用方式。

------

## 功能概览 

**ΣData** 提供以下核心功能，助您轻松管理和检索交易数据：

- **获取数据**：支持获取历史和实时的 **OHLCV 数据** 和 **历史交易数据（Trades）**。
- **管理数据**：通过基于 Numpy 的高效存储和检索优化，提高数据访问速度。
- **异步支持**：灵活适配高性能与高并发场景，同时提供同步和异步处理能力。

!!! note "适用场景"
	 **ΣData** 适用于量化回测、实时交易等场景。

------

## 数据获取  

### 1. 获取 OHLCV 数据  

**描述：**  通过 `DataManager` 的 `get_data` 方法，可高效获取多周期、多品种的历史 OHLCV 数据。  

#### 功能说明  

- 支持多周期、多品种的历史 OHLCV 数据获取。  
- 自动处理时间范围并补全缺失数据。  
- 自动存储至数据库，确保数据持久化。  

!!! warning "注意事项"  
    1. **API 限制：** 各交易所的 `limit` 参数数值不同，设置错误可能导致数据不完整。以下为部分交易所的默认值：  
        - OKX：100  
        - Binance：1000  
        - Bitget：200  
    2. **字段要求：** `columns` 参数中必须包含 `timestamp` 或 `date` 字段之一，否则返回的数据无法排序。若两者均未指定，系统默认返回 `date` 字段。  
    3. **实例化建议：** 推荐使用预初始化的交易所实例 (`ccxt.Exchange`) 来配置 `DataManager`，以确保更高效的资源管理和速率限制。  


#### 示例代码

##### 同步方式

```python 
from sigmadata import DataManager
from sigmalog import LoguruConfig              # 使用 sigmalog 配置日志

LoguruConfig.load("./configs/log_config.json") # 配置日志

def main():

    # 配置 DataManager 类初始化参数
    exchange = "bitget"                        # 交易所的名称
    param = {
        "httpsProxy": "http://127.0.0.1:7890",
        "wsProxy": "http://127.0.0.1:7890",
    }										   # 初始化交易所的参数。
    db_path = "./db/crypto_data.db"            # SQLite 数据库文件的路径
    db_check_same_thread = False               # SQLite 的 check_same_thread 参数，如果用于多线程则需要开启

    # 配置 get_data 方法参数
    symbol = "BTC/USDT:USDT"                   # 交易对符号
    timeframe = "15m"                          # OHLCV 数据的时间框架
    start_date = "2023-10-06T16:00:00.00Z"     # 起始日期，使用 ISO8601 格式。
    end_date = "2024-11-07T12:05:00.00Z"       # 结束日期，使用 ISO8601 格式。
    # end_date = None                          # 如果未指定，将默认为最新时间。
    price_type = 'default'                     # 价格数据类型
    limit = 200                                # 每次 API 调用要检索的最大数据点数量
    columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                                               # 要返回的列的列表

    # 初始化 DataManager 实例
    dm = DataManager(
        exchange_name=exchange, 
        exchange_param=param, 
        db_path=db_path,
        db_check_same_thread = db_check_same_thread
    )                                          

    # 调用 get_data 方法获取数据
    df = dm.get_data(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        price_type=price_type,
        limit=limit,
        columns=columns,
    )

    # 输出数据、保存数据到csv文件
    print(df)
    df.to_csv(f"btc_usdt_{timeframe}_data.csv", index=False)


if __name__ == "__main__":
    main()

```
##### 异步方式

```python 
import asyncio
import sys
from sigmadata.async_support.data_manager import DataManager # 通过 async_support 导入异步版本的 DataManager
from sigmalog import LoguruConfig

LoguruConfig.load("./configs/log_config.json")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():

    exchange = "bitget"                        
    param = {
        "httpsProxy": "http://127.0.0.1:7890",
        "wsProxy": "http://127.0.0.1:7890",
    }										   
    db_path = "./db/crypto_data.db"            

    symbol = "BTC/USDT:USDT"                   
    timeframe = "15m"                          
    start_date = "2023-10-06T16:00:00.00Z"     
    end_date = "2024-11-07T12:05:00.00Z"               
    price_type = 'default'                     
    limit = 200                                
    columns = ['date', 'open', 'high', 'low', 'close', 'volume']

    dm = DataManager(
        exchange_name=exchange, 
        exchange_param=param, 
        db_path=db_path
    )  
    await dm.open()                            # 初始化异步 DataManager

    # 调用异步 get_data 方法获取数据
    df = await dm.get_data(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        price_type=price_type,
        limit=limit,
        columns=columns,
    )                                        

    print(df)
    df.to_csv(f"btc_usdt_{timeframe}_data.csv", index=False)

    await dm.close()                            # 关闭异步 DataManager


if __name__ == "__main__":
    asyncio.run(main())

```

##### 使用预初始化的交易所实例

通过预先初始化交易所实例，可以在特定环境中手动管理交易所的激活状态，有效利用 CCXT 提供的速率限制功能，从而避免因请求速率过高导致的封禁风险。我们建议采用预初始化交易所实例的方式，以提高系统的稳定性和安全性。

```python 
from sigmadata import DataManager
from sigmalog import LoguruConfig

LoguruConfig.load("./configs/log_config.json")

def main():

    exchange = "bitget"                        
    param = {
        "httpsProxy": "http://127.0.0.1:7890",
        "wsProxy": "http://127.0.0.1:7890",
        # 'enableRateLimit': True,       # 默认启用
    }
    exchange = ccxt.bitget(param)        # 预先初始化 exchange
    db_path = "./db/crypto_data.db"            
    db_check_same_thread = False           

    symbol = "BTC/USDT:USDT"        
    timeframe = "15m"                      
    start_date = "2023-10-06T16:00:00.00Z"     
    end_date = "2024-11-07T12:05:00.00Z"          
    price_type = 'default'                     
    limit = 200                              
    columns = ['date', 'open', 'high', 'low', 'close', 'volume']

    dm = DataManager(
        exchange_name=exchange, 
        exchange=exchange,               # 传入预先初始化的 exchange
        db_path=db_path,
        db_check_same_thread = db_check_same_thread
    )                                          

    df = dm.get_data(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        price_type=price_type,
        limit=limit,
        columns=columns,
    )

    print(df)
    df.to_csv(f"btc_usdt_{timeframe}_data.csv", index=False)


if __name__ == "__main__":
    main()
```


### 2. 获取 Trades 数据（开发中）

---

## 数据管理

### 1. 管理 OHLCV 数据

**描述**：`Data` 类用于管理 OHLCV 数据。该类提供高效的数据操作方法，包括数据的初始化、添加、更新、删除以及清空等功能。`Data` 类支持线程安全的操作，并允许注册回调函数，以便在数据发生变化时异步通知外部组件，实现响应式编程模式。数据可以从多种来源初始化，包括 Pandas DataFrame、NumPy ndarray 或列表。

#### 功能说明

- **初始化数据**：使用 `init` 方法初始化 `Data` 实例，加载初始的 OHLCV 数据集。
- **添加数据**：使用 `add` 方法向数据集中添加新的 OHLCV 数据点。支持单条或多条数据的添加。
- **更新数据**：使用 `update` 方法更新数据集中的最新数据点，以确保数据的准确性。
- **删除数据**：使用 `remove` 方法删除数据集中的最新数据点，或使用 `clear` 方法清空整个数据集。
- **注册回调**：使用 `register_callback_sync` 和 `register_callback` 方法注册同步或异步回调函数，以便在数据发生变化时接收通知。
- **等待回调**：使用 `wait_for_callbacks` 和 `wait_for_callbacks_async` 方法等待所有提交的回调任务完成。
- **数据访问**：通过属性如 `timestamp`、`open`、`high`、`low`、`close`、`volume`、`df` 和 `np` 等获取数据的不同视图。
- **容量管理**：`Data` 类支持设置数据存储的最大容量，并在容量达到上限时，根据配置删除最旧的数据点或自动扩展存储容量。

!!! warning "注意事项"
	 当前 `add` 方法仅支持单条数据的添加，原因是受限于 `indicator` 中的增量计算逻辑，该逻辑目前仅支持对单条数据进行处理。

#### 使用示例

##### 1. 初始化 Data 实例

```python
from sigmadata import Data, EventType

iimport pandas as pd
import numpy as np

# 创建 Data 实例，设置容量为 1000，删除大小为 100
data_instance = Data(capacity=1000, delete_size=100)
```

##### 2. 初始化数据

```python
# 数据格式为 [timestamp, open, high, low, close, volume]

# 1. 使用列表初始化数据
initial_data = [
    [20230101, 100.0, 105.0, 99.0, 103.0, 1000],
    [20230102, 104.0, 107.0, 102.0, 106.0, 1500],
]
data_instance.init(initial_data)

# 2. 使用 Pandas DataFrame 初始化数据
df_initial = pd.DataFrame({
    'timestamp': [20230103, 20230104],
    'open': [106.0, 108.0],
    'high': [109.0, 111.0],
    'low': [104.0, 107.0],
    'close': [108.0, 110.0],
    'volume': [1200, 1300]
})
data_instance.init(df_initial)

# 3. 使用 NumPy ndarray 初始化数据
import numpy as np

array_initial = np.array([
    [20230105, 110.0, 115.0, 109.0, 114.0, 1400],
    [20230106, 112.0, 118.0, 111.0, 117.0, 1600]
])
data_instance.init(array_initial)
```

##### 3. 添加数据

```python
# 1. 添加单条数据，使用 Pandas Series
new_point_series = pd.Series({
    'timestamp': 20230107,
    'open': 114.0,
    'high': 119.0,
    'low': 113.0,
    'close': 118.0,
    'volume': 1700
})
data_instance.add(new_point_series)

# 2. 添加单条数据，使用列表
new_point_list = [20230108, 118.0, 120.0, 117.0, 119.0, 1800]
data_instance.add(new_point_list)

# 3. 添加单条数据，使用 Pandas DataFrame
new_point_df = pd.DataFrame({
    'timestamp': [20230109],
    'open': [119.0],
    'high': [121.0],
    'low': [118.0],
    'close': [120.0],
    'volume': [1900]
})
data_instance.add(new_point_df)

# 4. 添加单条数据，使用 NumPy ndarray
array_new = np.array([
    [20230110, 120.0, 125.0, 119.0, 124.0, 2000]
])
data_instance.add(array_new)
```

##### 4. 更新数据

```python
# 1. 更新最新数据，使用 Pandas Series
updated_point_series = pd.Series({
    'timestamp': 20230112,
    'open': 125.0,
    'high': 135.0,
    'low': 124.0,
    'close': 134.0,
    'volume': 2450
})
data_instance.update(updated_point_series)

# 2. 更新最新数据，使用列表
updated_point_list = [20230112, 125.0, 136.0, 124.0, 135.0, 2500]
data_instance.update(updated_point_list)

# 3. 更新最新数据，使用 NumPy ndarray
array_updated = np.array([20230112, 125.0, 137.0, 124.0, 136.0, 2550])
data_instance.update(array_updated)
```

##### 5. 删除数据

```python
# 删除最新数据点
data_instance.remove()

# 清空倒数后10个数据点
data_instance.clear(10)

# 清空所有数据点
data_instance.clear()
```

##### 6. 注册和注销回调

```python
# 定义一个回调函数
def on_data_event(event_type, data):
    print(f"事件类型: {event_type}, 当前数据量: {data.size}")

# 注册同步回调
data_instance.register_callback_sync(on_data_event)

# 注册多线程异步回调
data_instance.register_callback(on_data_event)

# 注销同步回调
data_instance.unregister_callback_sync(on_data_event)

# 注销多线程异步回调
data_instance.unregister_callback(on_data_event)
```

##### 7. 等待回调完成

```python
from concurrent.futures import FIRST_COMPLETED

# 等待所有回调任务完成
data_instance.wait_for_callbacks()

# 等待至少一个回调任务完成
data_instance.wait_for_callbacks(return_when=FIRST_COMPLETED)

# 异步等待所有回调任务完成（需要在异步环境中使用）
await data_instance.wait_for_callbacks_async()

# 异步等待至少一个回调任务完成（需要在异步环境中使用）
await data_instance.wait_for_callbacks_async(return_when=FIRST_COMPLETED)
```

##### 8. 访问数据

```python
# 获取时间戳
timestamps = data_instance.timestamp
print(timestamps)

# 获取开盘价
open_prices = data_instance.open
print(open_prices)

# 获取最高价
high_prices = data_instance.high
print(high_prices)

# 获取最低价
low_prices = data_instance.low
print(low_prices)

# 获取收盘价
close_prices = data_instance.close
print(close_prices)

# 获取成交量
volumes = data_instance.volume
print(volumes)

# 获取整个数据集的 NumPy 数组的可读视图
np_array = data_instance.np
print(np_array)

# 获取整个数据集的 Pandas DataFrame
df = data_instance.df
print(df)

# 获取数据集的容量
print(data_instance.capacity)

# 获取删除大小
print(data_instance.delete_size)

# 获取当前数据点数量
print(data_instance.size)

# 获取列名
print(data_instance.columns)

# 使用索引访问数据
first_row = data_instance[0]
print(first_row)

# 使用切片访问数据
subset = data_instance[1:3]
print(subset)

# 使用列表索引访问数据
specific_rows = data_instance[[0, 2]]
print(specific_rows)

# 获取 Data 实例的字符串表示
print(data_instance)
```



------

### 2. 管理 Trades 数据（开发中）

