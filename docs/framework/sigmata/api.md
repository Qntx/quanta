# API 接口文档

## Class `IndicatorManager`

------

`IndicatorManager` 管理一组金融指标，根据依赖关系对它们进行分类，并相应地处理数据事件。

`IndicatorManager` 类处理各种 `Indicator` 实例的生命周期，确保指标之间的依赖关系得到尊重。它监听来自 `Data` 类的数据事件，并触发适当的指标更新。该管理器支持同步和异步等待指标处理任务完成。

??? note "Class IndicatorManager 类图"
    ```mermaid
    classDiagram
        %% 类名
        class IndicatorManager {
            %% 外部属性
            +names : List~str~
            +indicators : List~Indicator~
            +root_indicators : List~Indicator~
            +dependent_indicators : List~Indicator~
            +dict : Dict~str, Indicator~
            +status : List~dict~
            %% 私有属性
            -_data : Data
            -_lock : threading.RLock
            -_executor : concurrent.futures.Executor
            -_root_indicators : List~Indicator~
            -_dependent_indicators : List~Indicator~
            -_indicators_dict : Dict~str, Indicator~
            -_root_indicators_futures : List~Future~
            -_dependent_indicators_futures : List~Future~
            %% 外部方法
            +__init__()
            +add_indicator()
            +remove_indicator()
            +get_indicator()
            +I()
            +synchronize()
            +synchronize_async()
            %% 私有方法
            -_register_dependent_future()
            -_on_data_changed()
            -_safe_execute()
        }
    ```



------

### 外部接口

#### **外部方法**

##### 1. `__init__`

```python
def __init__(self, data: Data)
```

**功能说明**: 使用指定的数据实例初始化 `IndicatorManager`，设置数据处理、注册回调，并准备内部结构以管理指标。

**参数**:

| 参数   | 类型   | 描述                             |
| ------ | ------ | -------------------------------- |
| `data` | `Data` | 用于管理金融数据的 `Data` 实例。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 2. `add_indicator`

```python
def add_indicator(self, indicator: Indicator, dependent: Optional[Indicator] = None)
```

**功能说明**: 在确保指标名称唯一的前提下，将指标添加到管理器中。如果指定了依赖项，则将指标分类为依赖指标并进行关联。

**参数**:

| 参数        | 类型                  | 描述                       |
| ----------- | --------------------- | -------------------------- |
| `indicator` | `Indicator`           | 要添加的指标实例。         |
| `dependent` | `Optional[Indicator]` | 该指标依赖的现有指标实例。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                                                         |
| ------------ | ------------------------------------------------------------ |
| `ValueError` | 如果具有相同名称的指标已存在，或者指定的依赖指标不存在，则抛出此异常。 |

------

##### 3. `remove_indicator`

```python
def remove_indicator(self, indicator: Indicator)
```

**功能说明**: 从管理器中移除一个指标，并从内部字典中删除其条目。如果该指标被分类为根指标或依赖指标，则从相应的列表中移除。

**参数**:

| 参数        | 类型        | 描述               |
| ----------- | ----------- | ------------------ |
| `indicator` | `Indicator` | 要移除的指标实例。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述                                   |
| -------- | -------------------------------------- |
| 无       | 如果尝试移除不存在的指标，将记录警告。 |

------

##### 4. `get_indicator`

```python
def get_indicator(self, name: str) -> Optional[Indicator]
```

**功能说明**: 根据唯一名称检索一个指标。

**参数**:

| 参数   | 类型  | 描述                 |
| ------ | ----- | -------------------- |
| `name` | `str` | 要检索的指标的名称。 |

**返回值**:

| 类型                  | 描述                                      |
| --------------------- | ----------------------------------------- |
| `Optional[Indicator]` | 如果找到，返回指标实例；否则返回 `None`。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 5. `I`

```python
def I(
    self,
    name: str,
    class_name: Type[Indicator],
    dependent: Optional[Indicator] = None,
    *args,
    **kwargs,
) -> Indicator
```

**功能说明**: 动态创建指定类的指标实例，并在管理器中进行管理。确保指标名称唯一，并处理依赖关系（如果提供）。

**参数**:

| 参数         | 类型                  | 描述                               |
| ------------ | --------------------- | ---------------------------------- |
| `name`       | `str`                 | 指标实例的唯一名称。               |
| `class_name` | `Type[Indicator]`     | 要实例化的指标类。                 |
| `dependent`  | `Optional[Indicator]` | 该新指标依赖的现有指标实例。       |
| `*args`      | `Any`                 | 传递给指标类构造函数的位置参数。   |
| `**kwargs`   | `Any`                 | 传递给指标类构造函数的关键字参数。 |

**返回值**:

| 类型        | 描述                   |
| ----------- | ---------------------- |
| `Indicator` | 创建并管理的指标实例。 |

**异常**:

| 异常类型     | 描述                                         |
| ------------ | -------------------------------------------- |
| `ValueError` | 如果具有指定名称的指标已存在，则抛出此异常。 |

------

##### 6. `synchronize`

```python
def synchronize(
    self,
    data_return_when=FIRST_COMPLETED,
    return_when=ALL_COMPLETED
)
```

**功能说明**: 同步等待所有提交的指标计算任务完成。此方法首先根据指定的 `data_return_when` 条件等待所有与数据相关的回调任务完成，然后根据 `return_when` 条件等待所有待处理的指标处理任务完成。

**参数**:

| 参数               | 类型                                 | 描述                                                         |
| ------------------ | ------------------------------------ | ------------------------------------------------------------ |
| `data_return_when` | `concurrent.futures.ReturnCondition` | 指定等待数据回调任务完成的条件。默认值为 `FIRST_COMPLETED`。 |
| `return_when`      | `concurrent.futures.ReturnCondition` | 指定等待指标处理任务完成的条件。默认值为 `ALL_COMPLETED`。   |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 7. `synchronize_async`

```python
async def synchronize_async(
    self,
    data_return_when=FIRST_COMPLETED,
    return_when=ALL_COMPLETED
)
```

**功能说明**: 异步等待所有提交的指标计算任务完成，而不会阻塞事件循环。此方法首先根据指定的 `data_return_when` 条件等待所有与数据相关的回调任务完成，然后根据 `return_when` 条件异步等待所有待处理的指标处理任务完成。

**参数**:

| 参数               | 类型                                 | 描述                                                         |
| ------------------ | ------------------------------------ | ------------------------------------------------------------ |
| `data_return_when` | `concurrent.futures.ReturnCondition` | 指定等待数据回调任务完成的条件。默认值为 `FIRST_COMPLETED`。 |
| `return_when`      | `concurrent.futures.ReturnCondition` | 指定等待指标处理任务完成的条件。默认值为 `ALL_COMPLETED`。   |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

#### **属性**

##### 1. `status`

```python
@property
def status(self) -> List[dict]
```

**功能说明**: 获取每个受管指标的状态。状态包括指标的名称、当前大小、容量、依赖关系、子指标以及初始化状态。

**返回值**:

| 类型         | 描述                     |
| ------------ | ------------------------ |
| `List[dict]` | 每个指标状态的字典列表。 |

??? note "返回值示例"
    返回值参数解释：

    - name: 指标的名称，用于标识具体指标实例。
    - size: 当前指标中存储的数据条数，反映存储的实际内容量。
    - capacity: 指标实例的存储容量上限，表示可以存储的最大数据条数。
    - dependencies: 该指标所依赖的其他指标的名称，列表形式。
    - sub_indicators: 子指标列表，指与该指标关联的其他指标。
    - initialized: 指标是否完成初始化，true 表示已初始化，false 表示未初始化。
    
    ```json
    [
        {
            "name": "SMA_50",
            "size": 150,
            "capacity": 1000,
            "dependencies": [], 
            "sub_indicators": ["EMA_20"],
            "initialized": True
        },
        ...
        {
            "name": "RSI_14",
            "size": 0,
            "capacity": 1000,
            "dependencies": ["EMA_20"], 
            "sub_indicators": [],
            "initialized": False
        }
    ]
    ```

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 2. `names`

```python
@property
def names(self) -> List[str]
```

**功能说明**: 获取管理器中所有指标的名称列表。

**返回值**:

| 类型        | 描述                 |
| ----------- | -------------------- |
| `List[str]` | 所有指标名称的列表。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 3. `indicators`

```python
@property
def indicators(self) -> List[Indicator]
```

**功能说明**: 获取管理器中所有指标实例的列表。

**返回值**:

| 类型              | 描述                          |
| ----------------- | ----------------------------- |
| `List[Indicator]` | 所有 `Indicator` 实例的列表。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 4. `root_indicators`

```python
@property
def root_indicators(self) -> List[Indicator]
```

**功能说明**: 获取所有根指标实例（即没有依赖的指标）。

**返回值**:

| 类型              | 描述                            |
| ----------------- | ------------------------------- |
| `List[Indicator]` | 所有根 `Indicator` 实例的列表。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 5. `dependent_indicators`

```python
@property
def dependent_indicators(self) -> List[Indicator]
```

**功能说明**: 获取所有依赖指标实例（即有依赖的指标）。

**返回值**:

| 类型              | 描述                              |
| ----------------- | --------------------------------- |
| `List[Indicator]` | 所有依赖 `Indicator` 实例的列表。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 6. `dict`

```python
@property
def dict(self) -> Dict[str, Indicator]
```

**功能说明**: 获取一个字典，所有指标实例按其唯一名称进行索引。

**返回值**:

| 类型                   | 描述                           |
| ---------------------- | ------------------------------ |
| `Dict[str, Indicator]` | 将指标名称映射到其实例的字典。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

### 内部实现

#### 内部方法

##### 1. `_register_dependent_future`

```python
def _register_dependent_future(
    self, _: EventType, indicator_instance: Indicator
) -> None
```

**功能说明**: 注册来自依赖指标实例的 `Future` 对象。此方法作为回调函数，在依赖指标完成其处理后被调用。它收集相关的 `Future` 对象，并将其添加到管理器的依赖指标 `Future` 列表中，以便后续的同步和监控。

**参数**:

| 参数                 | 类型        | 描述                                             |
| -------------------- | ----------- | ------------------------------------------------ |
| `_`                  | `EventType` | 触发此回调的事件类型（未使用）。                 |
| `indicator_instance` | `Indicator` | 触发回调的指标实例，包含要注册的 `Future` 对象。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 2. `_on_data_changed`

```python
def _on_data_changed(self, event_type: EventType, data_instance: Data)
```

**功能说明**: 当底层数据发生变化时调用的回调方法。根据数据事件的类型，此方法触发所有根指标的相应更新方法。它将数据事件映射到指标方法，并使用共享执行器异步提交这些方法的执行任务。执行过程中发生的任何异常都会被安全地处理和记录。

**参数**:

| 参数            | 类型        | 描述                     |
| --------------- | ----------- | ------------------------ |
| `event_type`    | `EventType` | 发生的数据事件类型。     |
| `data_instance` | `Data`      | 触发事件的 `Data` 实例。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述                             |
| -------- | -------------------------------- |
| 无       | 无（内部方法通过日志记录异常）。 |

------

##### 3. `_safe_execute`

```python
@staticmethod
def _safe_execute(method, *args)
```

**功能说明**: 安全地执行一个方法，捕获并记录执行过程中发生的任何异常。此静态方法用于以受控方式执行指标更新方法，确保异常不会中断整体应用流程。

**参数**:

| 参数     | 类型       | 描述               |
| -------- | ---------- | ------------------ |
| `method` | `Callable` | 要执行的方法。     |
| `*args`  | `Any`      | 传递给方法的参数。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述                               |
| -------- | ---------------------------------- |
| 无       | 异常在内部被捕获并记录，不会抛出。 |

------

#### 内部属性

| 属性名                          | 类型                   | 描述                                               |
| ------------------------------- | ---------------------- | -------------------------------------------------- |
| `_data`                         | `Data`                 | 管理 OHLCV 金融数据的单例 `Data` 实例。            |
| `_lock`                         | `threading.RLock`      | 可重入锁，用于确保线程安全的操作。                 |
| `_executor`                     | `ThreadPoolExecutor`   | 用于异步任务执行的共享执行器。                     |
| `_root_indicators`              | `List[Indicator]`      | 不依赖其他指标的根指标列表。                       |
| `_dependent_indicators`         | `List[Indicator]`      | 依赖其他指标的依赖指标列表。                       |
| `_indicators_dict`              | `Dict[str, Indicator]` | 通过唯一名称索引的所有指标。                       |
| `_root_indicators_futures`      | `List[Future]`         | 存储待处理的根指标计算任务的 `Future` 对象列表。   |
| `_dependent_indicators_futures` | `List[Future]`         | 存储待处理的依赖指标计算任务的 `Future` 对象列表。 |

---

## Class `Indicator`

------

`Indicator` 是一个用于高性能金融或技术指标的抽象基类。该类旨在高效处理时间序列数据，支持增量更新并确保线程安全。它作为实现各种需要实时数据处理和分析的金融指标的基础。

??? note "Class Indicator 类图"
    ```mermaid
    classDiagram
        class Indicator {
            %% 外部属性
            +values : np.ndarray
            +timestamps : np.ndarray
            +dict : Dict~str, List~float~~ abstract
            %% 私有属性
            -_lock : threading.RLock
            -_executor : concurrent.futures.Executor
            -_name : str
            -_capacity : int
            -_delete_size : int
            -_pre_process : Callable~[np.ndarray], np.ndarray~~
            -_post_process : Callable~[np.ndarray], np.ndarray~~
            -_size : int
            -_dependencies : List~Indicator~
            -_sub_indicators : List~Indicator~
            -_callbacks_sync : List~Callable~[[EventType, Indicator], None]~
            -_callbacks : List~Callable~[[EventType, Indicator], None]~
            -_dependent_indicators_futures : List~Future~
            -_callbacks_futures : List~Future~
            -_values : np.ndarray
            -_timestamps : np.ndarray
            %% 外部方法
            +__init__()
            +add_sub_indicator()
            +add_dependency()
            +init()
            +add()
            +update()
            +remove()
            +clear()
            +register_callback_sync()
            +unregister_callback_sync()
            +register_callback()
            +unregister_callback()
            %% 私有方法
            -_default_pre_process() (abstract)
            -_default_post_process() (abstract)
            -_compute_init_func() (abstract)
            -_compute_incremental_func() (abstract)
            -_notify_callbacks_sync()
            -_notify_callbacks()
            -_ensure_capacity()
            -_delete_oldest()
            -_expand_capacity()
        }
    ```



------

### 外部接口

#### **外部方法**

##### 1. `__init__`

```python
def __init__(
    self,
    name: str,
    capacity: int = 1000,
    delete_size: Optional[int] = None,
    pre_process: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    post_process: Optional[Callable[[np.ndarray], np.ndarray]] = None,
)
```

**功能说明**: 初始化 `Indicator`，包括存储分配、时间戳管理和线程同步机制。

**参数**:

| 参数           | 类型                                                         | 描述                                                         |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `name`         | `str`                                                        | 指标的名称。                                                 |
| `capacity`     | `int`（可选，默认：`1000`）                                  | 内部存储数组的初始容量。                                     |
| `delete_size`  | `Optional[int]`（可选，默认：`None`）                        | 当容量超出时要删除的最旧数据点数量。如果为 `None`，容量将根据需要扩展。 |
| `pre_process`  | `Optional[Callable[[np.ndarray], np.ndarray]]`（可选，默认：`None`） | 在计算前对输入数据进行预处理的函数。如果未提供，将使用默认的预处理方法。 |
| `post_process` | `Optional[Callable[[np.ndarray], np.ndarray]]`（可选，默认：`None`） | 在计算后对结果进行后处理的函数。如果未提供，将使用默认的后处理方法。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 2. `_default_pre_process`

```python
@staticmethod
@abstractmethod
def _default_pre_process(data: np.ndarray) -> np.ndarray:
    pass
```

**功能说明**: 默认的预处理函数，用于准备输入数据以进行计算。

**参数**:

| 参数   | 类型         | 描述                                           |
| ------ | ------------ | ---------------------------------------------- |
| `data` | `np.ndarray` | 输入数据数组，形状为 `(n_samples, features)`。 |

**返回值**:

| 类型         | 描述                 |
| ------------ | -------------------- |
| `np.ndarray` | 预处理后的数据数组。 |

**异常**:

| 异常类型 | 描述                                   |
| -------- | -------------------------------------- |
| 无       | 无（该方法为抽象方法，需由子类实现）。 |

------

##### 3. `_default_post_process`

```python
@staticmethod
@abstractmethod
def _default_post_process(values: np.ndarray) -> np.ndarray:
    pass
```

**功能说明**: 默认的后处理函数，用于完成计算后的指标值。

**参数**:

| 参数     | 类型         | 描述             |
| -------- | ------------ | ---------------- |
| `values` | `np.ndarray` | 计算出的指标值。 |

**返回值**:

| 类型         | 描述                   |
| ------------ | ---------------------- |
| `np.ndarray` | 后处理后的指标值数组。 |

**异常**:

| 异常类型 | 描述                                   |
| -------- | -------------------------------------- |
| 无       | 无（该方法为抽象方法，需由子类实现）。 |

------

##### 4. `_compute_init_func`

```python
@abstractmethod
def _compute_init_func(
    self, output_array: np.ndarray, input_data: np.ndarray, index: int
) -> None:
    pass
```

**功能说明**: 指标值初始化计算的抽象方法。

**参数**:

| 参数           | 类型         | 描述                           |
| -------------- | ------------ | ------------------------------ |
| `output_array` | `np.ndarray` | 用于存储计算出的指标值的数组。 |
| `input_data`   | `np.ndarray` | 用于计算的输入数据。           |
| `index`        | `int`        | 新数据点插入的位置索引。       |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述                                   |
| -------- | -------------------------------------- |
| 无       | 无（该方法为抽象方法，需由子类实现）。 |

------

##### 5. `_compute_incremental_func`

```python
@abstractmethod
def _compute_incremental_func(
    self, output_array: np.ndarray, input_data: np.ndarray, index: int
) -> None:
    pass
```

**功能说明**: 指标值增量更新计算的抽象方法。

**参数**:

| 参数           | 类型         | 描述                           |
| -------------- | ------------ | ------------------------------ |
| `output_array` | `np.ndarray` | 用于存储计算出的指标值的数组。 |
| `input_data`   | `np.ndarray` | 新的数据点用于计算。           |
| `index`        | `int`        | 新数据点插入的位置索引。       |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述                                   |
| -------- | -------------------------------------- |
| 无       | 无（该方法为抽象方法，需由子类实现）。 |

------

##### 6. `init`

```python
def init(
    self, data: np.ndarray, timestamps: np.ndarray, call_callbacks: bool = True
) -> None:
```

**功能说明**: 使用完整的数据集初始化指标，并计算所有初始值。

**参数**:

| 参数             | 类型                         | 描述                                                     |
| ---------------- | ---------------------------- | -------------------------------------------------------- |
| `data`           | `np.ndarray`                 | 用于指标初始化的输入数据集。形状应与指标预期的输入对齐。 |
| `timestamps`     | `np.ndarray`                 | 输入数据对应的时间戳。必须与 `data` 长度相同。           |
| `call_callbacks` | `bool`（可选，默认：`True`） | 是否在初始化后触发回调事件。                             |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                                       |
| ------------ | ------------------------------------------ |
| `ValueError` | 如果 `data` 和 `timestamps` 的长度不匹配。 |

------

##### 7. `add`

```python
def add(
    self, data: np.ndarray, timestamp: int, call_callbacks: bool = True
) -> None:
```

**功能说明**: 使用新的数据点增量更新指标。

**参数**:

| 参数             | 类型                         | 描述                                                         |
| ---------------- | ---------------------------- | ------------------------------------------------------------ |
| `data`           | `np.ndarray`                 | 用于计算下一个指标值的新数据点。形状应与指标预期的输入对齐。 |
| `timestamp`      | `int`                        | 新数据点对应的时间戳。                                       |
| `call_callbacks` | `bool`（可选，默认：`True`） | 是否在更新后触发回调事件。                                   |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 8. `update`

```python
def update(
    self, data: np.ndarray, timestamp: int, call_callbacks: bool = True
) -> None:
```

**功能说明**: 使用新的输入数据更新最后一个计算的指标值。如果没有数据存在，则表现为 `add` 方法。

**参数**:

| 参数             | 类型                         | 描述                                                         |
| ---------------- | ---------------------------- | ------------------------------------------------------------ |
| `data`           | `np.ndarray`                 | 用于重新计算和更新最后一个指标值的新数据。形状应与指标预期的输入对齐。 |
| `timestamp`      | `int`                        | 新数据点对应的时间戳。                                       |
| `call_callbacks` | `bool`（可选，默认：`True`） | 是否在更新后触发回调事件。                                   |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 9. `remove`

```python
def remove(self, call_callbacks: bool = True) -> None:
```

**功能说明**: 移除最后一个计算的指标值及其对应的时间戳。

**参数**:

| 参数             | 类型                         | 描述                       |
| ---------------- | ---------------------------- | -------------------------- |
| `call_callbacks` | `bool`（可选，默认：`True`） | 是否在移除后触发回调事件。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 10. `clear`

```python
def clear(self, amount: Optional[int] = None, call_callbacks: bool = True) -> None:
```

**功能说明**: 清除指定数量的计算值或全部值。

**参数**:

| 参数             | 类型                         | 描述                                                |
| ---------------- | ---------------------------- | --------------------------------------------------- |
| `amount`         | `Optional[int]`              | 要清除的最近值的数量。如果为 `None`，则清除所有值。 |
| `call_callbacks` | `bool`（可选，默认：`True`） | 是否在清除后触发回调事件。                          |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 11. `register_callback_sync`

```python
def register_callback_sync(
    self, callback: Callable[[EventType, "Indicator"], None]
) -> None
```

**功能说明**: 注册一个同步回调函数，当特定数据事件发生时被通知。

**参数**:

| 参数       | 类型                                       | 描述                   |
| ---------- | ------------------------------------------ | ---------------------- |
| `callback` | `Callable[[EventType, "Indicator"], None]` | 要注册的同步回调函数。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型    | 描述                                   |
| ----------- | -------------------------------------- |
| `TypeError` | 如果提供的 `callback` 不是可调用对象。 |

------

##### 12. `unregister_callback_sync`

```python
def unregister_callback_sync(
    self, callback: Callable[[EventType, "Indicator"], None]
) -> None
```

**功能说明**: 取消注册一个先前注册的同步回调函数。

**参数**:

| 参数       | 类型                                       | 描述                       |
| ---------- | ------------------------------------------ | -------------------------- |
| `callback` | `Callable[[EventType, "Indicator"], None]` | 要取消注册的同步回调函数。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                                     |
| ------------ | ---------------------------------------- |
| `ValueError` | 如果回调函数未在已注册的同步回调中找到。 |

------

##### 13. `register_callback`

```python
def register_callback(
    self, callback: Callable[[EventType, "Indicator"], None]
) -> None
```

**功能说明**: 注册一个回调函数，当特定数据事件发生时被异步通知。

**参数**:

| 参数       | 类型                                       | 描述               |
| ---------- | ------------------------------------------ | ------------------ |
| `callback` | `Callable[[EventType, "Indicator"], None]` | 要注册的回调函数。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型    | 描述                                   |
| ----------- | -------------------------------------- |
| `TypeError` | 如果提供的 `callback` 不是可调用对象。 |

------

##### 14. `unregister_callback`

```python
def unregister_callback(
    self, callback: Callable[[EventType, "Indicator"], None]
) -> None
```

**功能说明**: 取消注册一个先前注册的回调函数。

**参数**:

| 参数       | 类型                                       | 描述                   |
| ---------- | ------------------------------------------ | ---------------------- |
| `callback` | `Callable[[EventType, "Indicator"], None]` | 要取消注册的回调函数。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型     | 描述                                 |
| ------------ | ------------------------------------ |
| `ValueError` | 如果回调函数未在已注册的回调中找到。 |

------

##### 15. `add_sub_indicator`

```python
def add_sub_indicator(self, indicator: "Indicator") -> None
```

**功能说明**: 向当前指标添加一个子指标。

子指标用于基于主指标的数据计算相关的度量。当主指标的数据发生变化时，子指标将自动接收更新以确保其计算结果的及时性和准确性。

**参数**:

| 参数        | 类型        | 描述                 |
| ----------- | ----------- | -------------------- |
| `indicator` | `Indicator` | 要添加的子指标实例。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 16. `add_dependency`

```python
def add_dependency(self, indicator: "Indicator") -> None
```

**功能说明**: 为当前指标添加一个依赖指标。

通过添加依赖指标，当前指标将成为所提供依赖指标的子指标。这确保了当前指标在依赖指标更新后能够接收到最新的数据，从而维持其计算结果的准确性。

**参数**:

| 参数        | 类型        | 描述                           |
| ----------- | ----------- | ------------------------------ |
| `indicator` | `Indicator` | 当前指标依赖的另一个指标实例。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

#### **属性**

##### 1. `values`

```python
@property
def values(self) -> np.ndarray:
```

**功能说明**: 获取截至当前大小的计算指标值的只读副本。

**返回值**:

| 类型         | 描述               |
| ------------ | ------------------ |
| `np.ndarray` | 指标值的只读视图。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 2. `timestamps`

```python
@property
def timestamps(self) -> np.ndarray:
```

**功能说明**: 获取截至当前大小的时间戳的只读副本。

**返回值**:

| 类型         | 描述               |
| ------------ | ------------------ |
| `np.ndarray` | 时间戳的只读视图。 |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 3. `dict`

```python
@property
@abstractmethod
def dict(self) -> Dict[str, List[float]]:
```

**功能说明**: 将内部的 NumPy 数组转换为字典格式。

**返回值**:

| 类型                     | 描述                                               |
| ------------------------ | -------------------------------------------------- |
| `Dict[str, List[float]]` | 内部数据的字典表示，通常将字段名称映射到值的列表。 |

**异常**:

| 异常类型 | 描述                                   |
| -------- | -------------------------------------- |
| 无       | 无（该属性为抽象属性，需由子类实现）。 |

------

### 内部实现

#### 内部方法

##### 1. `_notify_callbacks_sync`

```python
def _notify_callbacks_sync(self, event_type: EventType) -> None
```

**功能说明**: 同步通知所有已注册的同步回调函数关于特定数据事件的发生。

此方法在特定事件（如初始化、添加、更新、移除或清除）发生时，按顺序调用所有注册的同步回调函数。它确保回调函数在主线程中执行，以维持线程安全性和数据一致性。

**参数**:

| 参数         | 类型        | 描述                 |
| ------------ | ----------- | -------------------- |
| `event_type` | `EventType` | 发生的数据事件类型。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 2. `_notify_callbacks`

```python
def _notify_callbacks(self, event_type: EventType) -> None
```

**功能说明**: 异步通知所有已注册的回调函数关于特定数据事件的发生。

此方法在特定事件发生时，异步调用所有注册的回调函数，避免阻塞主线程。回调函数的执行通过共享线程池进行管理，确保高效的并发处理。

**参数**:

| 参数         | 类型        | 描述                 |
| ------------ | ----------- | -------------------- |
| `event_type` | `EventType` | 发生的数据事件类型。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 3. `_ensure_capacity`

```python
def _ensure_capacity(self, n_new: int) -> None
```

**功能说明**: 确保内部存储有足够的容量来添加新的数据点。

当即将添加的新数据点数量导致总容量不足时，此方法会根据 `delete_size` 参数删除最旧的数据点，或根据需要扩展内部存储容量，以容纳新的数据点。

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

##### 4. `_delete_oldest`

```python
def _delete_oldest(self, delete_count: int) -> None
```

**功能说明**: 从内部存储中删除最旧的数据点。

此方法通过移除指定数量的最旧数据点来释放存储空间，并相应地更新内部的大小计数。删除操作会递归地应用于所有子指标，以保持数据的一致性。

**参数**:

| 参数           | 类型  | 描述                     |
| -------------- | ----- | ------------------------ |
| `delete_count` | `int` | 要删除的最旧数据点数量。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

##### 5. `_expand_capacity`

```python
def _expand_capacity(self, required_capacity: int) -> None
```

**功能说明**: 扩展内部存储容量以适应更多的数据点。

当当前容量不足以容纳新的数据点时，此方法将内部存储容量增加到至少满足 `required_capacity` 的需求。通常，容量会以倍增的方式扩展，以减少频繁的扩容操作，同时保留现有的数据。

**参数**:

| 参数                | 类型  | 描述                 |
| ------------------- | ----- | -------------------- |
| `required_capacity` | `int` | 需要达到的最小容量。 |

**返回值**:

| 类型   | 描述 |
| ------ | ---- |
| `None` | 无   |

**异常**:

| 异常类型 | 描述 |
| -------- | ---- |
| 无       | 无   |

------

#### 内部属性

| 属性名                          | 类型                                             | 描述                                               |
| ------------------------------- | ------------------------------------------------ | -------------------------------------------------- |
| `_lock`                         | `threading.RLock`                                | 可重入锁，用于确保线程安全的操作。                 |
| `_executor`                     | `ThreadPoolExecutor`                             | 用于异步任务执行的共享执行器。                     |
| `_name`                         | `str`                                            | 指标的名称。                                       |
| `_capacity`                     | `int`                                            | 内部存储数组的容量。                               |
| `_delete_size`                  | `Optional[int]`                                  | 当容量超出时要删除的最旧数据点数量。               |
| `_pre_process`                  | `Callable[[np.ndarray], np.ndarray]`             | 用于计算前的预处理函数。                           |
| `_post_process`                 | `Callable[[np.ndarray], np.ndarray]`             | 用于计算后的后处理函数。                           |
| `_size`                         | `int`                                            | 当前存储的指标值数量。                             |
| `_dependencies`                 | `List["Indicator"]`                              | 该指标依赖的其他指标列表。                         |
| `_sub_indicators`               | `List["Indicator"]`                              | 依赖于该指标的子指标列表。                         |
| `_callbacks_sync`               | `List[Callable[[EventType, "Indicator"], None]]` | 注册的同步回调函数列表。                           |
| `_callbacks`                    | `List[Callable[[EventType, "Indicator"], None]]` | 注册的异步回调函数列表。                           |
| `_dependent_indicators_futures` | `List[Future]`                                   | 存储待处理的依赖指标计算任务的 `Future` 对象列表。 |
| `_callbacks_futures`            | `List[Future]`                                   | 存储待处理的回调任务的 `Future` 对象列表。         |
| `_values`                       | `np.ndarray`                                     | 存储计算出的指标值的数组。                         |
| `_timestamps`                   | `np.ndarray`                                     | 存储对应时间戳的数组。                             |

