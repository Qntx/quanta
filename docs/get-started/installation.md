# ⚙️ 安装与配置

了解如何快速安装和配置 **Quantum**。

---

## 📦 系统要求

在安装之前，请确保你的环境满足以下要求：

| **要求**         | **最低要求**            | **推荐配置**                       |
| ---------------- | ----------------------- | ---------------------------------- |
| **操作系统**     | Windows / macOS / Linux | 最新版稳定系统                     |
| **Python**       | >= 3.10                 | 3.11                               |
| **依赖管理工具** | pip 或 poetry           | poetry                             |
| **硬件**         | 4-core CPU, 8GB RAM     | 12-core CPU, 16GB+ RAM, 16GB+ VRAM |

!!! note
    显卡不是必需的，但如果希望充分发挥功能，建议配备 Nvidia GPU，以显著提升性能。

---

## 🔧 安装方式

以下提供三种安装方式，推荐使用 **Docker 安装**。

---

### 1️⃣ 使用 Docker 构建（推荐）

使用 Docker 是安装和运行 Quantum 最简单且一致的方式。

#### 选择 Dockerfile 版本

根据你的硬件环境选择合适的 Dockerfile 构建镜像：

| **Dockerfile 版本** | **说明**                                        |
| ------------------- | ----------------------------------------------- |
| `Dockerfile`        | 仅支持 CPU 计算，适用于通用硬件环境             |
| `Dockerfile.cuda`   | 支持 NVIDIA GPU 计算，需安装 NVIDIA Docker 工具 |

#### 构建 CPU 版本的镜像

运行以下命令，基于 `Dockerfile.cpu` 构建镜像：

```bash
docker build -t quantum -f docker/Dockerfile .
```

#### 构建 GPU 版本的镜像（推荐）

如果你需要支持 NVIDIA GPU，运行以下命令基于 `Dockerfile.gpu` 构建镜像：

```bash
docker build -t quantum:cuda -f docker/Dockerfile.cuda .
```

!!! note 构建 
	Linux 系统上构建 GPU 版本需要预先安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)。确保你的环境支持 GPU Docker。

#### 启动容器

运行以下命令启动容器，并挂载所需的目录：

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/strategies:/app/strategies \
  quantum:cuda
```

进入容器后，你可以直接运行 Quantum 命令或脚本。

---

### 2️⃣ 使用 pip 安装

如果你希望直接在本地环境中安装 Quantum，可以使用以下命令通过 pip 进行安装：

```bash
pip install git+https://github.com/gitctrlx/Quantum.git
```

---

### 3️⃣ 本地开发安装

如果你计划参与 Quantum 的开发或希望查看源码，可以选择本地开发安装。


#### 克隆项目

从 GitHub 仓库克隆 Quantum 项目：

```bash
git clone https://github.com/qntx/Quantum.git
cd Quantum
```

!!! tip "推荐使用 SSH 克隆"
    如果你已配置 SSH 密钥，可以使用以下命令克隆：  

    ```bash
    git clone git@github.com:qntx/Quantum.git
    ```

#### 安装依赖

选择以下一种方法安装依赖：

- **使用 poetry（推荐）**
  ```bash
  poetry install
  poetry shell
  ```

- **使用 pip**
  ```bash
  pip install -r requirements.txt
  ```

---

## ✅ 测试安装

无论选择哪种安装方式，完成安装后可以运行以下命令测试安装是否成功：

```bash
qnta -v
```

如果安装成功，你将看到类似以下的输出：

```plaintext
Quantum version: 1.0.0
```

!!! info "版本检测失败？"
    如果命令未找到或输出错误，请检查以下内容：

    1. 环境是否正确配置
    2. Docker 容器是否正常运行
    3. pip 安装是否正确完成

---

## 📖 下一步

完成安装后，你可以：

1. 运行 [快速开始](./quick-start.md) 中的示例策略。
2. 探索 [详细使用说明](../tutorials/index.md)，了解更多高级功能。
3. 开始开发属于你的量化交易策略！

---

!!! success "完成安装"
    恭喜！你已成功安装和配置 Quantum。立即探索量化交易的无限可能吧！