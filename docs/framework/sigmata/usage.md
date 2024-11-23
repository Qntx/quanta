# 📘 使用指南 

欢迎来到 **ΣTA** 使用指南！本指南将详细介绍 **ΣTA** 的核心功能，包括如何

## 🌟 功能概览 

**ΣTA** 提供以下核心功能，：

- 

!!! note "适用场景"
	 **ΣTA** 适用于实时交易

```mermaid
classDiagram

    %% 定义 Data 类
    class Data {

        %% 外部属性
        +columns : List~str~
        +capacity : int
        +delete_size : int
        +size : int
        +timestamp : np.ndarray
        +open : np.ndarray
        +high : np.ndarray
        +low : np.ndarray
        +close : np.ndarray
        +volume : np.ndarray
        +np : np.ndarray
        +df : pd.DataFrame
        
        %% 内部属性
        -_lock : RLock
        -_executor : Executor
        -_callbacks_sync : List~Callable~[[EventType, Data], None]~
        -_callbacks : List~Callable~[[EventType, Data], None]~
        -_callback_futures : List~Future~

        %% 外部方法
        +__init__(capacity=1000, delete_size=100)
        +init(data, call_callbacks=True)
        +add(data, call_callbacks=True)
        +update(data, call_callbacks=True)
        +remove(call_callbacks=True)
        +clear(count=None, call_callbacks=True)
        +register_callback_sync(callback)
        +unregister_callback_sync(callback)
        +register_callback(callback)
        +unregister_callback(callback)
        +wait_for_callbacks(return_when=ALL_COMPLETED)
        +wait_for_callbacks_async(return_when=ALL_COMPLETED)
        
         %% 内部方法
        -_notify_callbacks_sync(event_type) : void
        -_notify_callbacks(event_type) : void
        -_process_input_data(data, single_row=False) : np.ndarray
        -_ensure_capacity(n_new) : void
        -_initialize_data(data) : np.ndarray
    }

```





``` mermaid
sequenceDiagram
  autonumber
  DataManager-->Data: Prepare data
  create participant IndicatorManager
  Data->>IndicatorManager: Define IndicatorManager and Define the indicators
  DataManager->>Data: Initialize the data for Data
  Data->>IndicatorManager: Submit task to initialize IndicatorManager
  IndicatorManager--)Data: Await all initialization tasks completion
  
  loop Data Modification and Indicator Update
      Data->>Data: Modify data (Add, Update, or Clear)
      Data->>IndicatorManager: Submit task for incremental indicator update
      IndicatorManager--)Data: Await with updated indicators
  end

```



??? note "详细的图表展示"
    ```mermaid
    sequenceDiagram
      autonumber
      DataManager->>DataManager: Load OHLCV Data
      DataManager-->Data: Prepare data
      create participant IndicatorManager
      Data->>IndicatorManager: Define IndicatorManager
      create participant Indicator
      IndicatorManager->>Indicator: Define the indicators
      DataManager->>Data: Initialize the data for Data
      Data->>GlobalThreadPool: Submit task to initialize IndicatorManager
      GlobalThreadPool-->>IndicatorManager: Submit initialization tasks to IndicatorManager
      IndicatorManager->>GlobalThreadPool: Submit tasks to initialize individual indicators
      par Initialize Indicator 1
          GlobalThreadPool-->>Indicator: Initialize Indicator 1
      and Initialize Indicator 2
          GlobalThreadPool-->>Indicator: Initialize Indicator 2
      and Initialize Indicator N
          GlobalThreadPool-->>Indicator: Initialize Indicator N
      end
      GlobalThreadPool--)IndicatorManager: Await all indicator initialization completion
      GlobalThreadPool--)Data: Await all initialization tasks completion
      loop Data Modification and Indicator Update
          Data->>Data: Modify data (Add, Update, or Clear)
          Data->>GlobalThreadPool: Submit task for incremental indicator update
          GlobalThreadPool-->>IndicatorManager: Submit incremental update tasks to IndicatorManage
          IndicatorManager->>GlobalThreadPool: Submit tasks to update individual indicators
          par Update Indicator 1
              GlobalThreadPool-->>Indicator: Update Indicator 1
          and Update Indicator 2
              GlobalThreadPool-->>Indicator: Update Indicator 2
          and Update Indicator N
              GlobalThreadPool-->>Indicator: Update Indicator N
          end
          GlobalThreadPool--)IndicatorManager: Await all updates completion
          GlobalThreadPool--)Data: Await with updated indicators
      end
    ```





