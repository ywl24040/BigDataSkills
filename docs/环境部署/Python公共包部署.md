# Python 公共包部署（bds_common）

## 1. 目标

在 `big-data-skills` 仓库中，公共能力（例如数据库配置加载、MySQL 连接创建）已经封装为可复用 Python 包：

- 包源码位置：`big-data-skills/common/python`
- Python 包名：`bds_common`
- 包发布名：`bds-common`

本文件记录如何在本地、Demo、以及交付场景中安装/打包/部署该公共包。

---

## 2. 目录结构约定（src 布局）

```text
big-data-skills/
└─ common/
   └─ python/
      ├─ pyproject.toml
      └─ src/
         └─ bds_common/
            ├─ __init__.py
            ├─ db_config_loader.py
            ├─ db_config.py
            └─ mysql.py
```

说明：

- 采用 `src/` 布局可避免“源码目录被误当成已安装包”导致的导入混乱
- 所有 Demo 都应通过 `pip install` 安装该包后再 import，而不是通过 `sys.path` 拼路径

---

## 3. 本地开发安装（推荐：Editable 安装）

适用场景：

- 在同一个仓库内开发 + 运行多个 Demo
- 希望修改公共包代码后，Demo 立刻生效

步骤：

1) 激活 conda 环境（示例为全局环境）

```bash
conda activate big-data-skills
```

2) 在仓库根目录执行 editable 安装

```bash
python -m pip install -e .\common\python
```

验证：

```bash
python -c "import bds_common; print(bds_common.DB_CONFIG.get('host'))"
```

---

## 4. Demo 项目使用方式（示例）

Demo 代码中不再维护各自的 `db_config.py`，统一改为：

### 4.1 获取 DB_CONFIG

```python
from bds_common import DB_CONFIG
```

### 4.2 创建 SQLAlchemy Engine（推荐）

```python
from bds_common import create_mysql_engine

engine = create_mysql_engine(section="dev")
```

### 4.3 创建 PyMySQL 连接（可选）

```python
from bds_common import create_pymysql_connection

conn = create_pymysql_connection(section="dev")
```

说明：

- `section` 对应 `config/db_config.ini` 里的配置段（dev/test/prod）
- 也可以通过环境变量 `DB_ENV` 控制默认环境

---

## 5. 配置文件部署建议（db_config.ini）

公共配置建议放在仓库级目录：

```text
big-data-skills/config/db_config.ini
```

建议策略：

- 提交到仓库的只保留 `db_config.example.ini`（模板）
- 真实 `db_config.ini` 放入 `.gitignore`（避免提交密码）
- 生产环境密码通过环境变量注入覆盖（如 `DB_PASSWORD`）

---

## 6. 打包发布（Wheel）

适用场景：

- 需要把公共包交付到其他机器/容器
- 需要在 CI 中生成制品
- 需要上传到企业私有 PyPI

在 `big-data-skills/common/python` 目录构建：

```bash
cd g:\DataSkills\big-data-skills\common\python
python -m pip install -U build
python -m build
```

输出位置：

```text
big-data-skills/common/python/dist/
  bds_common-0.1.0-py3-none-any.whl
  bds_common-0.1.0.tar.gz
```

安装 wheel（离线/交付机）：

```bash
python -m pip install dist\bds_common-0.1.0-py3-none-any.whl
```

---

## 7. CI/CD 部署建议（最小化）

推荐在 CI 流水线固定做以下步骤：

1. 创建/激活 conda 环境（或使用预置镜像）
2. 安装公共包（editable 或 wheel）
3. 运行 lint/test
4. 构建 wheel 并作为制品上传

示例命令（仅示意）：

```bash
python -m pip install -e common/python
ruff check .
pytest

cd common/python
python -m build
```

---

## 8. 生产部署建议（容器化思路）

如果最终要在容器中运行 Demo/作业，建议：

- 使用 `environment.yml` 创建 conda 环境（或在镜像构建阶段执行）
- 在镜像构建时安装 `bds-common` wheel（更稳定）
- 配置通过环境变量注入（DB_HOST/DB_USER/DB_PASSWORD 等）

核心原则：

- 依赖锁定
- 配置外置
- 构建一次，多环境复用
