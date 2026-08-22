# Python 企业级环境管理方案（Windows 版）

## 1. 目标

企业级 Python 环境管理的核心目标不是单纯安装 Python，而是解决以下问题：

- 不同项目之间依赖互不污染
- 团队成员开发环境尽量统一
- 测试环境、生产环境可复现
- 依赖版本可锁定、可追踪
- 新成员可以快速完成环境搭建
- 包下载源、凭据、内部组件可以统一治理

在 Windows 环境下，推荐优先采用一套简单、稳定、容易推广的方案。

---

## 2. 总体推荐方案

推荐使用以下组合：

- Python 版本管理：`pyenv-win` 或公司统一安装标准版本
- 虚拟环境管理：`venv`
- 依赖管理：`pip-tools`
- 项目描述：`pyproject.toml`
- 代码质量工具：`ruff`、`black`、`pytest`
- 提交检查：`pre-commit`
- 包源管理：企业私有 PyPI 镜像
- 交付方式：`Docker` 或固定运行机环境

如果团队当前还比较初级，可以先从下面这套最稳方案开始：

- Python
- venv
- pip
- requirements.in
- requirements.txt

这已经足够支撑大多数企业内部项目。

---

## 3. 企业级分层思路

### 3.1 Python 版本统一

建议：

- 团队统一主版本，例如 `Python 3.11.x`
- 所有项目尽量保持在同一大版本
- CI 环境必须与开发环境对齐

推荐做法：

- 新项目模板中明确写清 Python 版本
- 在 `README.md` 或 `pyproject.toml` 中声明版本要求

示例：

```toml
[project]
requires-python = ">=3.11,<3.12"
```

---

### 3.2 项目级虚拟环境隔离

Windows 企业开发中，最推荐使用：

- `python -m venv .venv`

优点：

- Python 官方标准方案
- 轻量、稳定
- 与大多数 IDE 兼容性好

不建议：

- 所有项目共用一个全局 Python site-packages
- 直接把三方包装到系统 Python 中

---

### 3.3 依赖锁定

企业环境最关键的一点就是：

- 依赖要能复现

推荐使用：

- `requirements.in` 维护直接依赖
- `pip-compile` 生成锁定版 `requirements.txt`

示例：

`requirements.in`

```text
pandas
sqlalchemy
pymysql
pytest
ruff
```

生成锁定依赖：

```powershell
pip-compile requirements.in -o requirements.txt
```

安装依赖：

```powershell
pip install -r requirements.txt
```

这样做的好处：

- 直接依赖和间接依赖分离
- 团队成员安装结果一致
- CI 安装结果一致

---

## 4. 推荐目录结构

```text
project/
├─ .venv/
├─ src/
│  └─ your_app/
├─ tests/
├─ scripts/
├─ .gitignore
├─ .pre-commit-config.yaml
├─ pyproject.toml
├─ requirements.in
├─ requirements.txt
└─ README.md
```

说明：

- `.venv/`：虚拟环境目录
- `src/`：业务代码
- `tests/`：测试代码
- `scripts/`：辅助脚本
- `requirements.in`：直接依赖
- `requirements.txt`：锁定依赖

---

## 5. Windows 环境落地步骤

### 5.1 安装标准 Python

建议：

- 安装统一版本，例如 `Python 3.11`
- 勾选加入 PATH
- 使用公司统一文档或统一安装包

验证：

```powershell
python --version
pip --version
```

---

### 5.2 创建项目虚拟环境

```powershell
python -m venv .venv
```

激活环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果使用 cmd：

```bat
.\.venv\Scripts\activate.bat
```

#### 5.2.1 常见问题：`Activate.ps1` 报错（执行策略限制）

现象：

- 执行 `.\.venv\Scripts\Activate.ps1` 提示无法加载脚本、系统禁止运行脚本等

推荐处理方式（仅当前窗口生效）：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

可选处理方式（对当前用户长期生效）：

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

不想使用 PowerShell 时可改用 `cmd`：

```bat
.\.venv\Scripts\activate.bat
```

---

### 5.3 安装基础工具

```powershell
pip install --upgrade pip
pip install pip-tools ruff black pytest pre-commit
```

---

### 5.4 维护依赖文件

创建 `requirements.in`：

```text
pandas
sqlalchemy
pymysql
pytest
ruff
black
```

生成锁定依赖：

```powershell
pip-compile requirements.in -o requirements.txt
```

#### 5.4.1 常见问题：`pip-compile` 命令找不到

现象：

- 提示无法将 `pip-compile` 识别为命令

优先检查：

1. 是否已经激活项目虚拟环境 `.venv`
2. 是否已经安装 `pip-tools`

安装 `pip-tools`（建议在虚拟环境内执行）：

```powershell
python -m pip install -U pip pip-tools
```

推荐使用模块方式执行（更稳定，避免 PATH 问题）：

```powershell
python -m piptools compile requirements.in -o requirements.txt
```

安装：

```powershell
pip install -r requirements.txt
```

#### 5.4.2 `requirements.in` 推荐放置位置

建议放在项目根目录，与 `requirements.txt`、`pyproject.toml` 同级，便于团队统一约定与 CI/CD 执行：

```text
project/
├─ requirements.in
├─ requirements.txt
├─ pyproject.toml
├─ README.md
├─ src/
└─ tests/
```

当存在开发依赖时，推荐拆分：

```text
project/
├─ requirements.in
├─ requirements-dev.in
├─ requirements.txt
└─ requirements-dev.txt
```

---

### 5.5 配置代码质量工具

建议启用：

- `ruff`：lint
- `black`：格式化
- `pytest`：测试
- `pre-commit`：提交前检查

安装 Git hooks：

```powershell
pre-commit install
```

---

## 6. `pyproject.toml` 推荐配置思路

示例：

```toml
[project]
name = "your-project"
version = "0.1.0"
requires-python = ">=3.11,<3.12"

[tool.black]
line-length = 88

[tool.ruff]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
```

作用：

- 统一项目元数据
- 集中管理工具配置
- 提升项目规范化程度

---

## 7. 企业私有包源方案

企业内部推荐统一接入：

- Nexus
- Artifactory
- 阿里云制品仓库

`pip.ini` 示例：

```ini
[global]
index-url = https://your-private-pypi/simple
trusted-host = your-private-pypi
```

建议：

- 开发机优先走内网私有源
- 生产环境禁止直接从公网下载依赖
- 内部公共包统一发布到私有源
- 建议在 CI 中显式指定包源与锁定依赖，避免不同构建机因为网络差异导致安装结果不一致

---

## 8. 企业内部公共组件管理

推荐将以下能力做成内部基础包：

- 日志组件
- 配置组件
- 数据库连接组件
- HTTP 客户端组件
- 监控埋点组件

优点：

- 项目复用率高
- 降低重复造轮子
- 提升团队一致性

---

## 9. 凭据与配置管理

不要把以下信息直接写死在代码中：

- 数据库密码
- API Token
- Access Key

推荐方案：

- `.env` 文件用于本地开发
- 环境变量用于测试和生产
- 密钥平台用于企业正式环境

本地示例：

```text
DB_HOST=192.168.1.10
DB_USER=demo
DB_PASSWORD=your-password
```

---

## 10. 企业级自动化建议

CI 流程建议固定为：

1. 创建虚拟环境
2. 安装锁定依赖
3. 执行代码检查
4. 执行测试
5. 构建交付物

常见命令：

```powershell
ruff check .
black --check .
pytest
```

---

## 11. Windows 环境推荐实践总结

如果你要在企业里落地一套稳妥方案，我建议直接采用：

- Python 3.11
- venv
- pip-tools
- requirements.in / requirements.txt
- pyproject.toml
- ruff + black + pytest
- pre-commit
- 私有 PyPI

这套方案的优点是：

- 工具简单
- 兼容性强
- 团队推广成本低
- 适合大多数企业 Python 项目

---

## 12. 最小可执行标准

如果先不追求特别复杂的企业平台能力，可以先统一以下标准：

1. 所有人使用相同 Python 版本
2. 每个项目必须使用 `.venv`
3. 所有依赖通过 `requirements.in` 和 `requirements.txt` 管理
4. 所有代码提交前执行 `ruff` 和 `pytest`
5. 所有依赖优先从企业私有源安装

做到这 5 条，已经是比较实用的企业级环境管理基础方案。
