# API 接口文档

## Class `DataManager`

`DataManager` 是一个数据管理系统，旨在高效处理加密货币数据的检索和存储。它利用数据库缓存来最小化冗余的 API 请求，从而优化数据获取过程。

------


### 外部接口

#### **外部方法**

##### 1. `__init__`

```python
def __init__(
    self,
    exchange_name: str,
    exchange_param: Optional[dict] = None,
    *,
    exchange: Optional[ccxt.Exchange] = None,
    db_path: str = "crypto_data.db",
    db_check_same_thread: bool = True,
)
```

**功能说明**: 使用指定的交易所和数据库配置初始化 `DataManager` 实例。

**参数**:

| 参数                   | 类型                      | 描述                                                   |
| ---------------------- | ------------------------- | ------------------------------------------------------ |
| `exchange_name`        | `str`                     | 交易所的名称（例如 `'binance'`）。此参数为必填项。     |
| `exchange_param`       | `Optional[dict]`          | 初始化交易所的参数。                                   |
| `exchange`             | `Optional[ccxt.Exchange]` | 预配置的 `ccxt.Exchange` 实例。                        |
| `db_path`              | `str`                     | SQLite 数据库文件的路径。默认值为 `"crypto_data.db"`。 |
| `db_check_same_thread` | `bool`                    | SQLite 的 `check_same_thread` 参数。默认值为 `True`。  |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                                                         |
| ------------ | ------------------------------------------------------------ |
| `ValueError` | 如果 `exchange_name` 为空或无效，或者提供的 `exchange` 实例无效。 |

------

##### 2. `get_data`

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
) -> pd.DataFrame:
```

**功能说明**: 为指定的交易对和时间框架检索 OHLCV 数据。它优先查询数据库，如有必要，则从交易所获取缺失的数据。

**参数**:

| 参数         | 类型                  | 描述                                                         |
| ------------ | --------------------- | ------------------------------------------------------------ |
| `symbol`     | `str`                 | 交易对符号（例如 `'BTC/USDT'`）。                            |
| `timeframe`  | `str`                 | OHLCV 数据的时间框架（`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d`, `3d`, `1w`, `1M`）。 |
| `start_date` | `str`                 | 起始日期，使用 ISO8601 格式。                                |
| `end_date`   | `Optional[str]`       | 结束日期，使用 ISO8601 格式。如果未指定，将默认为当前时间减去一个`timeframe`的间隔。 |
| `price_type` | `str`                 | 要获取的价格数据类型（`'default'`、`'mark'`、`'index'`、`'premiumIndex'`）。 |
| `limit`      | `int`                 | 每次 API 调用要检索的最大数据点数量。默认值为 `200`。        |
| `columns`    | `Optional[List[str]]` | 要返回的列的列表（ `['timestamp', 'date', 'open', 'high', 'low', 'close', 'volume']`） |

**返回值**:

| 类型           | 描述                                       |
| -------------- | ------------------------------------------ |
| `pd.DataFrame` | 包含请求的 OHLCV 数据的 Pandas DataFrame。 |

**异常**:

| 异常类型     | 描述                             |
| ------------ | -------------------------------- |
| `ValueError` | 如果 `end_date` 不是字符串类型。 |

!!! warning
    1. limit 的具体数值因不同交易所而不同，API 限制填写错误会导致数据获取不全，下面是几个交易所的数据： 
        - Binance 默认为 1000。 
        - OKX 默认为 100。 
        - Bitget 默认为 200。 
    2. columns 中必须包含 `timestamp` 或 `date` 其中一个，否则获取的数据没有顺序。如果两个都没有填写，默认返回 `date`。

------

### 内部实现

#### 内部方法

##### 1. `_query_existing_data`

```python
def _query_existing_data(
    self,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    price_type: str = "default",
    columns: Optional[List[str]] = None,
) -> pd.DataFrame:
```

**功能说明**: 从数据库中查询指定日期范围内的现有数据。

**参数**:

| 参数         | 类型                  | 描述                                                         |
| ------------ | --------------------- | ------------------------------------------------------------ |
| `symbol`     | `str`                 | 交易对符号（例如 `'BTC/USDT'`）。                            |
| `timeframe`  | `str`                 | OHLCV 数据的时间框架（例如 `'1m'`、`'1h'`、`'1d'`）。        |
| `start_date` | `str`                 | 起始日期，使用 ISO8601 格式。                                |
| `end_date`   | `str`                 | 结束日期，使用 ISO8601 格式。                                |
| `price_type` | `str`                 | 要获取的价格数据类型（`'default'`、`'mark'`、`'index'`、`'premiumIndex'`）。 |
| `columns`    | `Optional[List[str]]` | 要返回的列的列表。                                           |

**返回值**:

| 类型           | 描述                              |
| -------------- | --------------------------------- |
| `pd.DataFrame` | 包含现有数据的 Pandas DataFrame。 |

**异常**:

| 异常类型 | 描述                                           |
| -------- | ---------------------------------------------- |
| 无       | 无（内部方法主要记录日志，不会直接抛出异常）。 |

------

##### 2. `_fetch_and_store_data`

```python
def _fetch_and_store_data(
    self,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    limit: int,
    price_type: str,
) -> None:
```

**功能说明**: 从交易所获取数据并存储到数据库中。

**参数**:

| 参数         | 类型  | 描述                                  |
| ------------ | ----- | ------------------------------------- |
| `symbol`     | `str` | 交易对符号（例如 `'BTC/USDT'`）。     |
| `timeframe`  | `str` | OHLCV 数据的时间框架。                |
| `start_date` | `str` | 起始日期，使用 ISO8601 格式。         |
| `end_date`   | `str` | 结束日期，使用 ISO8601 格式。         |
| `limit`      | `int` | 每次 API 调用要检索的最大数据点数量。 |
| `price_type` | `str` | 要获取的价格数据类型。                |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述                                           |
| -------- | ---------------------------------------------- |
| 无       | 无（内部方法主要记录日志，不会直接抛出异常）。 |

------

##### 3. `_determine_missing_ranges`

```python
def _determine_missing_ranges(
    self,
    existing_data: pd.DataFrame,
    start_date: str,
    end_date: str,
    timeframe: str,
) -> List[Tuple[str, str]]:
```

**功能说明**: 确定需要从交易所获取的缺失数据范围。

**参数**:

| 参数            | 类型           | 描述                              |
| --------------- | -------------- | --------------------------------- |
| `existing_data` | `pd.DataFrame` | 包含现有数据的 Pandas DataFrame。 |
| `start_date`    | `str`          | 起始日期，使用 ISO8601 格式。     |
| `end_date`      | `str`          | 结束日期，使用 ISO8601 格式。     |
| `timeframe`     | `str`          | OHLCV 数据的时间框架。            |

**返回值**:

| 类型                    | 描述                                                         |
| ----------------------- | ------------------------------------------------------------ |
| `List[Tuple[str, str]]` | 包含缺失数据范围的元组列表，每个元组包含 `(start_date, end_date)`。 |

**异常**:

| 异常类型 | 描述                                           |
| -------- | ---------------------------------------------- |
| 无       | 无（内部方法主要记录日志，不会直接抛出异常）。 |

------

#### 内部属性

| 属性名           | 类型            | 描述                                   |
| ---------------- | --------------- | -------------------------------------- |
| `exchange_name`  | `str`           | 交易所的名称。                         |
| `exchange_param` | `dict`          | 初始化交易所时使用的参数。             |
| `exchange`       | `ccxt.Exchange` | 初始化后的 `ccxt.Exchange` 实例。      |
| `data_source`    | `CcxtSource`    | 数据源处理实例，用于从交易所获取数据。 |
| `db`             | `Database`      | 数据库处理实例，用于数据的存储和查询。 |

------

## Class `Data`

`Data` 是一个管理 OHLCV（开盘价、高点、低点、收盘价、交易量）金融数据的单例类，支持高效的数据存储与操作。通过预分配 NumPy 数组实现高性能的数据操作，同时支持异步事件回调，可在数据修改时触发预定义操作。

------

### 外部接口

#### 外部方法

##### 1. `__init__`

```python
def __init__(self, capacity: int = 1000, delete_size: int = 100)
```

**功能说明**: 初始化 `Data` 实例，但不加载数据。通过 `init` 方法填充数据集。

**参数**:

| 参数          | 类型  | 描述                                                         |
| ------------- | ----- | ------------------------------------------------------------ |
| `capacity`    | `int` | NumPy 数组的最大容量（最多存储的 OHLCV 数据点数量）。默认值为 `1000`。 |
| `delete_size` | `int` | 在数组满时删除的最旧数据点的数量。默认值为 `100`。           |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**: 无

##### 2. `init`

```python
def init(
    self,
    data: Union[pd.DataFrame, np.ndarray, List[List[Any]]],
    call_callbacks: bool = True,
)
```

**功能说明**: 使用 Pandas DataFrame、NumPy 数组或列表初始化数据。

**参数**:

| 参数             | 类型                                   | 描述                                                         |
| ---------------- | -------------------------------------- | ------------------------------------------------------------ |
| `data`           | `pd.DataFrame` / `np.ndarray` / `list` | 初始化的数据，必须包含以下列顺序：`[timestamp, open, high, low, close, volume]`。 |
| `call_callbacks` | `bool`（默认：`True`）                 | 是否在初始化时触发已注册的回调事件。                         |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                             |
| ------------ | -------------------------------- |
| `ValueError` | 如果数据格式错误或超出存储容量。 |
| `TypeError`  | 如果输入的数据类型不被支持。     |

------

##### 3. `add`

```python
def add(
    self,
    data: Union[pd.Series, pd.DataFrame, np.ndarray, List[Any]],
    call_callbacks: bool = True,
)
```

**功能说明**: 添加单条或多条新的 OHLCV 数据。此方法会确保容量足够，如容量不足，将自动移除最旧的数据点。

**参数**:

| 参数             | 类型                                                 | 描述                   |
| ---------------- | ---------------------------------------------------- | ---------------------- |
| `data`           | `pd.Series` / `pd.DataFrame` / `np.ndarray` / `list` | 添加的数据。           |
| `call_callbacks` | `bool`（默认：`True`）                               | 是否触发添加回调事件。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型       | 描述                     |
| -------------- | ------------------------ |
| `ValueError`   | 如果输入数据格式不正确。 |
| `RuntimeError` | 如果添加操作在内部出错。 |

!!! warning
	当前仅支持添加单条数据，因为与 Indicator 结合的增量计算一次只能计算一条数据。

------

##### 4. `update`

```python
def update(
    self,
    data: Union[pd.Series, np.ndarray, List[Any]],
    call_callbacks: bool = True,
)
```

**功能说明**: 更新最新的一条 OHLCV 数据。该方法会替换当前数据集中最后一条记录。

**参数**:

| 参数             | 类型                                | 描述                                 |
| ---------------- | ----------------------------------- | ------------------------------------ |
| `data`           | `pd.Series` / `np.ndarray` / `list` | 更新的数据，必须与当前最新数据匹配。 |
| `call_callbacks` | `bool`（默认：`True`）              | 是否触发更新回调事件。               |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                           |
| ------------ | ------------------------------ |
| `IndexError` | 当数据集中没有数据时无法更新。 |
| `ValueError` | 如果输入数据不符合格式。       |

------

##### 5. `remove`

```python
def remove(
    self, 
    call_callbacks: bool = True
)
```

**功能说明**: 删除数据集中最新的一条记录。如果当前数据集中没有数据，则抛出异常。

**参数**:

| 参数             | 类型                   | 描述                   |
| ---------------- | ---------------------- | ---------------------- |
| `call_callbacks` | `bool`（默认：`True`） | 是否触发删除回调事件。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                           |
| ------------ | ------------------------------ |
| `IndexError` | 当数据集中没有记录时无法删除。 |

------

##### 6. `clear`

```python
def clear(
    self, 
    count: Optional[int] = None, 
    call_callbacks: bool = True
)
```

**功能说明**: 清空数据集中指定数量的记录。如果未指定 `count` 参数，将删除所有记录。

**参数**:

| 参数             | 类型                   | 描述                                              |
| ---------------- | ---------------------- | ------------------------------------------------- |
| `count`          | `int`（可选）          | 要清空的记录数量。如果为 `None`，则清空所有数据。 |
| `call_callbacks` | `bool`（默认：`True`） | 是否在清空数据后触发回调事件。                    |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                             |
| ------------ | -------------------------------- |
| `ValueError` | 如果 `count` 为负值或不合法。    |
| `无`         | 无数据时触发回调，但无实际异常。 |

------

##### 7. `register_callback_sync`

```python
def register_callback_sync(
    self, 
    callback: Callable[[EventType, "Data"], None]
) -> None
```

**功能说明**: 注册一个同步回调函数，用于在数据事件发生时触发。

**参数**:

| 参数       | 类型                                  | 描述                   |
| ---------- | ------------------------------------- | ---------------------- |
| `callback` | `Callable[[EventType, "Data"], None]` | 要注册的同步回调函数。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型    | 描述                                   |
| ----------- | -------------------------------------- |
| `TypeError` | 如果提供的 `callback` 不是可调用对象。 |

------

##### 8. `unregister_callback_sync`

```python
def unregister_callback_sync(
    self, 
    callback: Callable[[EventType, "Data"], None]
) -> None
```

**功能说明**: 取消注册一个同步回调函数。

**参数**:

| 参数       | 类型                                  | 描述                       |
| ---------- | ------------------------------------- | -------------------------- |
| `callback` | `Callable[[EventType, "Data"], None]` | 要取消注册的同步回调函数。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                           |
| ------------ | ------------------------------ |
| `ValueError` | 如果提供的 `callback` 未找到。 |

------

##### 9. `wait_for_callbacks`

```python
def wait_for_callbacks(
    self,
    return_when: Literal["ALL_COMPLETED", "FIRST_COMPLETED", "FIRST_EXCEPTION"] = "ALL_COMPLETED",
)
```

**功能说明**: 阻塞当前线程，直到所有提交的回调任务完成。

**参数**:

| 参数          | 类型                                                         | 描述                         |
| ------------- | ------------------------------------------------------------ | ---------------------------- |
| `return_when` | `Literal["ALL_COMPLETED", "FIRST_COMPLETED", "FIRST_EXCEPTION"]`（默认：`ALL_COMPLETED`） | 指定等待条件，决定何时返回。 |

**返回值**:

| 类型                      | 描述                                |
| ------------------------- | ----------------------------------- |
| `concurrent.futures.wait` | 根据 `return_when` 返回相应的结果。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 10. `wait_for_callbacks_async`

```python
async def wait_for_callbacks_async(
    self,
    return_when: Literal["ALL_COMPLETED", "FIRST_COMPLETED", "FIRST_EXCEPTION"] = "ALL_COMPLETED",
)
```

**功能说明**: 异步等待所有提交的回调任务完成。

**参数**:

| 参数          | 类型                                                         | 描述                         |
| ------------- | ------------------------------------------------------------ | ---------------------------- |
| `return_when` | `Literal["ALL_COMPLETED", "FIRST_COMPLETED", "FIRST_EXCEPTION"]`（默认：`ALL_COMPLETED`） | 指定等待条件，决定何时返回。 |

**返回值**:

| 类型                      | 描述                                |
| ------------------------- | ----------------------------------- |
| `concurrent.futures.wait` | 根据 `return_when` 返回相应的结果。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

#### 属性

| 属性名        | 类型           | 描述                                                         |
| ------------- | -------------- | ------------------------------------------------------------ |
| `timestamp`   | `np.ndarray`   | 返回 `timestamp` 列的只读 NumPy 数组，表示时间戳信息。       |
| `open`        | `np.ndarray`   | 返回 `open` 列的只读 NumPy 数组，表示开盘价。                |
| `high`        | `np.ndarray`   | 返回 `high` 列的只读 NumPy 数组，表示最高价。                |
| `low`         | `np.ndarray`   | 返回 `low` 列的只读 NumPy 数组，表示最低价。                 |
| `close`       | `np.ndarray`   | 返回 `close` 列的只读 NumPy 数组，表示收盘价。               |
| `volume`      | `np.ndarray`   | 返回 `volume` 列的只读 NumPy 数组，表示交易量。              |
| `np`          | `np.ndarray`   | 返回整个数据集的只读 NumPy 数组，包含 `[timestamp, open, high, low, close, volume]`。 |
| `df`          | `pd.DataFrame` | 返回整个数据集的 Pandas DataFrame 格式。                     |
| `size`        | `int`          | 当前存储的 OHLCV 数据点数量。                                |
| `capacity`    | `int`          | 数据实例的最大存储容量。                                     |
| `delete_size` | `int`          | 当容量达到上限时，每次删除的最旧数据点数量。                 |
| `columns`     | `List[str]`    | 返回  `["timestamp", "open", "high", "low", "close", "volume"]`。 |

------

### 内部实现

#### 内部方法

##### 1. `_initialize_data`

```python
def _initialize_data(
    self, data: Union[pd.DataFrame, np.ndarray, List[List[Any]]]
) -> np.ndarray:
```

**功能说明**: 将输入的数据（Pandas DataFrame、NumPy 数组或列表）转换为适合内部存储的 NumPy 数组，并验证数据的格式是否符合要求。

**参数**:

| 参数   | 类型                                   | 描述                                                         |
| ------ | -------------------------------------- | ------------------------------------------------------------ |
| `data` | `pd.DataFrame` / `np.ndarray` / `list` | 输入数据，必须包含以下列顺序：`[timestamp, open, high, low, close, volume]`。 |

**返回值**:

| 类型         | 描述                                   |
| ------------ | -------------------------------------- |
| `np.ndarray` | 转换后的 NumPy 数组，形状为 `(n, 6)`。 |

**异常**:

| 异常类型     | 描述                                                        |
| ------------ | ----------------------------------------------------------- |
| `ValueError` | 如果数据的形状或列名不符合要求，则抛出此异常。              |
| `TypeError`  | 如果输入的数据类型不是支持的类型（DataFrame、数组或列表）。 |

------

##### 2. `_ensure_capacity`

```python
def _ensure_capacity(self, n_new: int):
```

**功能说明**: 确保有足够的容量存储新数据。如果当前容量不足，将按照 `delete_size` 移除最旧的数据点以腾出空间。

**参数**:

| 参数    | 类型  | 描述                     |
| ------- | ----- | ------------------------ |
| `n_new` | `int` | 即将添加的新数据点数量。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 3. `_process_input_data`

```python
def _process_input_data(
    self,
    data: Union[pd.Series, pd.DataFrame, np.ndarray, List[Any]],
    single_row: bool = False,
) -> np.ndarray:
```

**功能说明**: 处理输入数据，验证其格式并将其转换为适合存储的 NumPy 数组。

**参数**:

| 参数         | 类型                                                 | 描述                                                     |
| ------------ | ---------------------------------------------------- | -------------------------------------------------------- |
| `data`       | `pd.Series` / `pd.DataFrame` / `np.ndarray` / `list` | 输入数据，支持单条或多条数据。                           |
| `single_row` | `bool`                                               | 是否为单条数据，若为 `True`，则确保数据形状为 `(1, 6)`。 |

**返回值**:

| 类型         | 描述                                                         |
| ------------ | ------------------------------------------------------------ |
| `np.ndarray` | 转换后的 NumPy 数组，单条数据为 `(1, 6)`，多条数据为 `(n, 6)`。 |

**异常**:

| 异常类型     | 描述                                                 |
| ------------ | ---------------------------------------------------- |
| `ValueError` | 如果输入数据的格式或形状不符合要求，则抛出此异常。   |
| `TypeError`  | 如果输入的数据类型不是支持的类型（如未指定的类型）。 |

------

##### 4. `_notify_callbacks_sync`

```python
def _notify_callbacks_sync(self, event_type: EventType) -> None:
```

**功能说明**: 同步通知所有已注册的同步回调函数，执行与指定事件类型相关的操作。

**参数**:

| 参数         | 类型        | 描述                                      |
| ------------ | ----------- | ----------------------------------------- |
| `event_type` | `EventType` | 触发事件的类型（如 `ADD`、`UPDATE` 等）。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述                                             |
| -------- | ------------------------------------------------ |
| 无       | 无（任何异常会被记录到日志中，但不会中断操作）。 |

------

##### 5. `_notify_callbacks`

```python
def _notify_callbacks(self, event_type: EventType):
```

**功能说明**: 异步通知所有已注册的回调函数，提交任务到线程池执行，避免阻塞主线程。

**参数**:

| 参数         | 类型        | 描述                                      |
| ------------ | ----------- | ----------------------------------------- |
| `event_type` | `EventType` | 触发事件的类型（如 `ADD`、`UPDATE` 等）。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述                                             |
| -------- | ------------------------------------------------ |
| 无       | 无（任何异常会被记录到日志中，但不会中断操作）。 |

------

#### 内部属性

| 属性名              | 类型                                        | 描述                                                         |
| ------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| `_lock`             | `threading.RLock`                           | 可重入锁，用于确保多线程操作的线程安全性。                   |
| `_executor`         | `concurrent.futures.ThreadPoolExecutor`     | 用于异步回调任务的共享线程池执行器。                         |
| `_np`               | `np.ndarray`                                | 预分配的 NumPy 数组，存储 OHLCV 数据，每行对应一个数据点，包含 `[timestamp, open, high, low, close, volume]`。 |
| `_callbacks_sync`   | `List[Callable[[EventType, "Data"], None]]` | 同步回调函数列表，当数据事件触发时，调用已注册的同步回调。   |
| `_callbacks`        | `List[Callable[[EventType, "Data"], None]]` | 异步回调函数列表，当数据事件触发时，异步调用已注册的回调。   |
| `_callback_futures` | `List[Future]`                              | 跟踪异步回调任务的 `Future` 对象列表，确保任务执行的监控与管理。 |

!!! note 
	使用预分配的 NumPy 数组来加快读写速度。
