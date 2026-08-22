# Python 企业级环境管理方案（Linux 版）

## 1. 目标

Linux 环境下的企业级 Python 环境管理，通常面向以下场景：

- 后端服务
- 定时任务
- 数据处理作业
- API 服务
- CI/CD 执行环境
- 容器化部署环境

核心目标仍然是：

- Python 版本统一
- 依赖隔离
- 依赖锁定
- 安装源可控
- 部署结果可复现

---

## 2. 总体推荐方案

Linux 环境推荐组合如下：

- Python 版本管理：`pyenv`
- 虚拟环境：`venv`
- 依赖管理：`pip-tools`
- 工具配置：`pyproject.toml`
- 代码质量：`ruff`、`black`、`pytest`
- 提交检查：`pre-commit`
- 私有包源：Nexus / Artifactory
- 交付方式：`Docker`

如果项目属于数据科学或 AI 场景，也可以考虑：

- `conda` / `mamba`

但对常规企业服务型项目，最推荐仍然是：

- `pyenv + venv + pip-tools`

---

## 3. 企业级分层思路

### 3.1 Python 版本管理

Linux 下最常用的是：

- `pyenv`

优点：

- 能并存多个 Python 版本
- 项目切换方便
- 与 CI、本地环境容易保持一致

建议：

- 统一团队主版本，例如 `3.11.x`
- 项目内放置 `.python-version`

示例：

```text
3.11.9
```

---

### 3.2 虚拟环境隔离

推荐：

```bash
python -m venv .venv
```

激活：

```bash
source .venv/bin/activate
```

企业开发中不建议：

- 直接把所有依赖装入系统 Python
- 多个项目共用一个虚拟环境

---

### 3.3 依赖锁定

最推荐的落地方式：

- `requirements.in`
- `requirements.txt`
- `pip-compile`

示例：

`requirements.in`

```text
fastapi
uvicorn
sqlalchemy
pymysql
pytest
ruff
```

生成：

```bash
pip-compile requirements.in -o requirements.txt
```

安装：

```bash
pip install -r requirements.txt
```

这样可以确保：

- 开发环境一致
- 测试环境一致
- 生产环境一致

---

## 4. 推荐目录结构

```text
project/
├─ .venv/
├─ src/
│  └─ your_app/
├─ tests/
├─ scripts/
├─ docker/
├─ .gitignore
├─ .pre-commit-config.yaml
├─ pyproject.toml
├─ requirements.in
├─ requirements.txt
├─ Dockerfile
└─ README.md
```

说明：

- `src/`：业务代码
- `tests/`：自动化测试
- `docker/`：容器相关脚本
- `requirements.in`：直接依赖
- `requirements.txt`：锁定依赖

---

## 5. Linux 环境落地步骤

### 5.1 安装基础系统依赖

不同 Linux 发行版需要先安装编译环境和 Python 相关依赖。

以 Ubuntu 为例：

```bash
sudo apt update
sudo apt install -y build-essential curl git \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev libffi-dev liblzma-dev tk-dev
```

作用：

- 为 Python 编译和部分三方包安装提供底层依赖

---

### 5.2 安装 pyenv

示例：

```bash
curl https://pyenv.run | bash
```

然后在 `~/.bashrc` 或 `~/.zshrc` 中加入：

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

刷新配置：

```bash
source ~/.bashrc
```

---

### 5.3 安装指定 Python 版本

```bash
pyenv install 3.11.9
pyenv local 3.11.9
```

验证：

```bash
python --version
pip --version
```

---

### 5.4 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 5.5 安装项目基础工具

```bash
pip install --upgrade pip
pip install pip-tools ruff black pytest pre-commit
```

---

### 5.6 管理项目依赖

创建 `requirements.in`：

```text
fastapi
uvicorn
sqlalchemy
pymysql
pytest
ruff
black
```

生成锁定依赖：

```bash
pip-compile requirements.in -o requirements.txt
```

安装依赖：

```bash
pip install -r requirements.txt
```

---

## 6. `pyproject.toml` 推荐配置

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

说明：

- 统一项目配置
- 集中管理代码工具参数
- 提高团队规范一致性

---

## 7. 私有包源配置

Linux 下推荐配置 `pip.conf`：

文件位置：

```text
~/.pip/pip.conf
```

示例：

```ini
[global]
index-url = https://your-private-pypi/simple
trusted-host = your-private-pypi
timeout = 60
```

建议：

- 所有开发机优先走企业私有源
- 生产环境禁止公网直连安装
- 内部包统一在私有仓库发布

---

## 8. 内部公共组件管理

企业中建议将以下通用能力封装成内部公共包：

- 配置管理
- 数据库访问
- 日志
- HTTP 请求
- 链路追踪
- 告警与监控

发布流程建议：

1. 内部基础包独立仓库维护
2. 通过 CI 自动构建 wheel
3. 发布到企业私有 PyPI
4. 业务项目按版本引用

---

## 9. 凭据与配置管理

不要在代码仓库中直接保存以下内容：

- 数据库密码
- Token
- Access Key
- SSH 私钥

推荐方案：

- 本地开发：`.env`
- 测试环境：环境变量
- 生产环境：配置中心或密钥平台

示例：

```bash
export DB_HOST=192.168.1.10
export DB_USER=demo
export DB_PASSWORD=your-password
```

---

## 10. Docker 与运行环境统一

Linux 企业项目非常推荐使用 Docker 做最终交付。

最核心的价值是：

- 开发、测试、生产环境更一致
- Python 版本和系统依赖一起固定
- 部署可复制

示例思路：

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "-m", "your_app"]
```

建议：

- 容器中安装锁定依赖
- 镜像构建过程固定
- 配置通过环境变量注入

---

## 11. CI/CD 推荐流程

Linux 下的 CI 流程建议为：

1. 拉取代码
2. 选择固定 Python 版本
3. 创建虚拟环境
4. 安装锁定依赖
5. 执行 lint
6. 执行测试
7. 构建 Docker 镜像
8. 发布制品

常见命令：

```bash
ruff check .
black --check .
pytest
```

---

## 12. Linux 环境推荐实践总结

如果你要在企业 Linux 环境里落地，我最推荐的组合是：

- pyenv
- venv
- pip-tools
- pyproject.toml
- 私有 PyPI
- ruff + black + pytest
- pre-commit
- Docker

适合场景：

- 后端服务
- ETL 作业
- 定时任务
- 数据平台脚本
- 内部 API 服务

---

## 13. 最小可执行标准

如果先从务实角度落地，可以先统一以下规则：

1. 所有项目统一 Python 版本
2. 每个项目必须独立 `.venv`
3. 所有依赖必须锁定到 `requirements.txt`
4. 所有依赖优先从企业私有源安装
5. 所有提交至少经过 `ruff` 和 `pytest`
6. 所有生产部署通过 Docker 或统一运行环境执行

这 6 条已经足够构成一套很实用的 Linux 企业级 Python 环境管理方案。
