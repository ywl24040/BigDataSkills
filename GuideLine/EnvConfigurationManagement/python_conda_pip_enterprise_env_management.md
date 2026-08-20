# Python 企业级环境管理方案（Conda + Pip 落地版）

## 1. 适用场景

Conda + pip 组合在企业中很常见，尤其适合以下场景：

- 数据分析/ETL（pandas、numpy、pyarrow 等二进制依赖多）
- 机器学习/科学计算（scipy、pytorch、opencv 等）
- Windows 环境下 C 扩展安装容易踩坑的项目
- 需要跨平台（Windows/Linux）较稳定的依赖安装体验

如果项目是纯后端服务、依赖偏纯 Python（fastapi、django 等），也能用 conda，但通常 `venv + pip-tools` 更轻量。

---

## 2. 核心原则（企业落地必须统一）

### 2.1 先 conda，后 pip

- conda 负责安装“底层大件/二进制依赖/编译复杂”的包
- pip 只负责补齐“纯 Python 包/conda 缺失的包/企业内部包”

不要反过来用 pip 覆盖 conda 已经安装的核心包（例如 numpy/pandas），否则容易出现环境不一致或运行时崩溃。

### 2.2 固定 channel 策略

建议团队统一采用：

- `conda-forge`（生态完整、更新快）

并避免在同一环境里混用多个 channel（特别是 defaults + conda-forge 混用）导致的依赖冲突。

### 2.3 pip 必须在 conda 环境内运行

推荐统一命令写法：

```bash
python -m pip install ...
```

这样可以确保 pip 装到当前 conda 环境，而不是误装到系统 Python 或别的环境。

### 2.4 交付物必须可复现

企业级要求不是“我装好了”，而是“任何人按文件即可复现同一套环境”。

最低要求：

- 使用 `environment.yml` 管理 conda + pip 依赖

更强要求：

- 使用 lock 文件（例如 `conda-lock`）锁定到具体构建产物

---

## 3. 推荐依赖划分（怎么决定用 conda 还是 pip）

### 3.1 优先用 conda 安装的包（示例）

- Python 本体：`python`
- 科学计算底座：`numpy`、`pandas`、`scipy`
- 数据处理二进制：`pyarrow`、`lxml`
- 数据库驱动（视情况）：`mysqlclient`（如果需要）

### 3.2 优先用 pip 安装的包（示例）

- 纯 Python 工具链：`ruff`、`black`、`pytest`、`pre-commit`、`pip-tools`
- Web/业务依赖（通常 conda 也有，但 pip 更主流）：`fastapi`、`pydantic`、`requests`
- 企业内部包（通常以 wheel/sdist 的形式发布到私有 PyPI）

---

## 4. 标准落地流程（推荐）

### 4.1 安装 conda（推荐 Miniconda）

本方案推荐安装 Miniconda（轻量，只包含 conda）。以下提供 Windows / Linux 两套安装方式。

#### 4.1.1 Windows 安装（Miniconda）

方式 A：图形界面安装（推荐）

1. 打开 Miniconda 下载页（选择 Windows x86_64）：
   - https://docs.conda.io/en/latest/miniconda.html
2. 下载后双击安装：
   - 建议安装到有权限的目录，例如 `C:\Users\<你>\Miniconda3` 或 `D:\Miniconda3`
   - “Add Miniconda3 to my PATH”一般不建议勾选（避免污染系统 PATH）
3. 安装完成后，打开 “Anaconda Prompt (Miniconda3)” 验证：

```powershell
conda --version
conda info
```

如果在 PowerShell 里用不了 conda（常见于未初始化）：

```powershell
conda init powershell
```

然后关闭并重新打开 PowerShell，再执行 `conda --version`。

#### 4.1.2 Linux 安装（Miniconda）

下载并执行安装脚本（以 x86_64 为例）：

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

安装过程中会询问安装目录，常见使用：

- `~/miniconda3`

安装完成后初始化 shell：

```bash
~/miniconda3/bin/conda init
```

重新打开终端后验证：

```bash
conda --version
conda info
```

#### 4.1.3 安装后建议操作

建议更新一次 conda：

```bash
conda update -n base -c defaults conda -y
```

---

### 4.2 创建环境（固定 Python 版本）

```bash
conda create -n etl_demo python=3.12 -y
conda activate etl_demo
```

验证：

```bash
python --version
python -m pip --version
```

### 4.3 先用 conda 安装基础依赖

建议统一使用 conda-forge：

```bash
conda install -c conda-forge pandas numpy sqlalchemy pymysql -y
```

### 4.4 再用 pip 补齐工具链和缺失依赖

```bash
python -m pip install -U pip
python -m pip install ruff black pytest pre-commit pip-tools
```

---

## 5. `environment.yml`（推荐作为团队标准交付物）

建议项目内维护一份 `environment.yml`，包含 conda 依赖和 pip 依赖。

示例（适用于 pandas + MySQL ETL 项目）：

```yaml
name: etl_demo
channels:
  - conda-forge
dependencies:
  - python=3.12
  - pandas
  - numpy
  - sqlalchemy
  - pymysql
  - pip
  - pip:
      - ruff
      - black
      - pytest
      - pre-commit
      - pip-tools
```

创建环境：

```bash
conda env create -f environment.yml
conda activate etl_demo
```

更新环境（增删依赖后）：

```bash
conda env update -f environment.yml --prune
```

---

## 6. 锁版本与可复现（进阶）

### 6.1 什么时候需要 lock

当出现以下情况，建议引入 lock：

- 团队成员多、环境差异导致问题频繁
- 生产环境要求强一致
- 构建机/镜像构建要求完全可复现

### 6.2 推荐工具：conda-lock

思路：

1. 维护 `environment.yml`（表达“我想要什么”）
2. 生成 lock 文件（锁到“装到什么具体包”）
3. CI 和生产环境优先使用 lock 来创建环境

---

## 7. 与 pip-tools 的配合方式（可选）

如果团队希望对 pip 依赖也做更严格的锁定，可以采用：

- conda 负责大件依赖
- pip-tools 负责 pip 依赖锁定

一种可落地结构：

```text
project/
├─ environment.yml               # conda 依赖 + pip 入口（pip 部分可只写 pip-tools）
├─ requirements.in               # pip 直接依赖（纯 Python/业务包）
├─ requirements.txt              # pip 锁定依赖（由 pip-tools 生成）
└─ ...
```

生成 pip 锁定依赖（推荐模块方式执行，避免命令找不到）：

```bash
python -m piptools compile requirements.in -o requirements.txt
```

安装 pip 锁定依赖：

```bash
python -m pip install -r requirements.txt
```

---

## 8. 企业网络与私有源（必须统一）

### 8.1 conda 私有镜像

企业内网建议统一 conda 镜像源（如有），并在团队文档中固定配置方式。

### 8.2 pip 私有 PyPI

企业内推荐统一使用私有 PyPI（Nexus/Artifactory/云制品库），避免公网不稳定与供应链风险。

建议：

- 开发、CI、生产都从同一私有源安装
- 对生产环境禁止公网直连安装依赖

---

## 9. 常见问题与排查

### 9.1 pip 出现 hash 校验失败（THESE PACKAGES DO NOT MATCH THE HASHES）

常见原因：

- pip 被全局配置了 `require-hashes`
- 使用了 requirements/constraints 文件并包含 hash
- 更换了 pip 源或镜像导致下载到的构建产物不同

建议处理思路：

1. 优先统一 pip 源与依赖锁定策略
2. 不建议直接删除 hash 强行安装
3. 必要时重新生成锁定文件（由工具生成，不手改）

### 9.2 环境变“玄学”的典型原因

- pip 覆盖了 conda 安装的 numpy/pandas
- 混用多个 conda channel
- 同一个环境里反复升级/降级，导致依赖解算结果漂移

---

## 10. 最小企业落地标准（建议写进团队规范）

1. 每个项目必须独立 conda 环境（禁止共用 base）
2. 固定 Python 主版本（例如 3.12）
3. 固定 conda channel（推荐 conda-forge）
4. pip 必须通过 `python -m pip` 执行
5. 项目必须提供 `environment.yml` 作为交付文件
6. CI 环境按 `environment.yml`（或 lock 文件）创建环境并执行测试与代码检查
