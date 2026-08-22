# `etl_to_db.py` 逐步学习笔记

对应源码文件：

- [etl_to_db.py](file:///g:/DataSkills/big-data-skills/Python_Pandas/ETL_DEMO1_FULL_LOAD/Code/Python/AI/etl_to_db.py)

## 1. 这个脚本是做什么的

这个脚本是整个练习项目里最核心的部分。

它做了 5 件事：

1. 读取 `raw_orders.csv`
2. 清洗数据
3. 把清洗后的结果保存成 `clean_orders.csv`
4. 在 MySQL 中重建目标表
5. 把清洗后的数据写入 MySQL

你可以把它理解成：

- `generate_data.py` 是“造原始数据”
- `etl_to_db.py` 是“清洗并入库”

---

## 2. 源码逐段解释

### 第 1-8 行：导入模块

```python
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from bds_common import DB_CONFIG
```

解释：

- `from pathlib import Path`
  - 用来处理文件路径
  - 后面会定位 `raw_orders.csv` 和 `clean_orders.csv`

- `from urllib.parse import quote_plus`
  - 用来对密码做 URL 编码
  - 因为数据库连接字符串里如果密码包含特殊字符，可能会出问题
  - `quote_plus()` 可以把这些字符转成更安全的格式

- `import pandas as pd`
  - 导入 `pandas`
  - 后面读取 CSV、转换日期、清洗数据都靠它

- `from sqlalchemy import create_engine, text`
  - `create_engine`：创建数据库连接引擎
  - `text`：执行原始 SQL 语句时会用到

- `from sqlalchemy.exc import SQLAlchemyError`
  - 导入数据库异常类
  - 后面如果数据库连接失败，可以捕获错误并给出更友好的提示

- `from bds_common import DB_CONFIG`
  - 从公共包 `bds_common` 中读取数据库配置（统一从仓库级配置文件加载）
  - 包括主机、端口、用户名、密码、数据库名等

---

### 第 11-13 行：定义文件路径

```python
BASE_DIR = Path(__file__).resolve().parent
RAW_FILE = BASE_DIR / "raw_orders.csv"
CLEAN_FILE = BASE_DIR / "clean_orders.csv"
```

解释：

- `BASE_DIR = Path(__file__).resolve().parent`
  - 获取当前脚本所在目录

- `RAW_FILE = BASE_DIR / "raw_orders.csv"`
  - 原始文件路径

- `CLEAN_FILE = BASE_DIR / "clean_orders.csv"`
  - 清洗后文件路径

这 3 行的作用是：

- 不管你从哪个目录运行脚本
- 它都能在当前项目目录中找到文件

---

### 第 16-26 行：解析混合日期格式

```python
def parse_mixed_date(value: object) -> pd.Timestamp:
    if pd.isna(value):
        return pd.NaT

    text_value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        parsed = pd.to_datetime(text_value, format=fmt, errors="coerce")
        if not pd.isna(parsed):
            return parsed

    return pd.NaT
```

解释：

- `def parse_mixed_date(value: object) -> pd.Timestamp:`
  - 定义一个函数，用来处理日期字段
  - 输入是一个值，输出是 Pandas 的日期类型

- `if pd.isna(value):`
  - 判断这个值是不是空值
  - 比如空单元格、缺失值

- `return pd.NaT`
  - `NaT` 可以理解为“时间类型的空值”
  - 类似数字里的 `NaN`

- `text_value = str(value).strip()`
  - 先把值转成字符串
  - 再去掉前后空格

- `for fmt in (...):`
  - 循环尝试 3 种日期格式：
    - `2024-01-15`
    - `2024/01/15`
    - `15-01-2024`

- `parsed = pd.to_datetime(text_value, format=fmt, errors="coerce")`
  - 用当前格式尝试解析日期
  - `errors="coerce"` 的意思是：
    - 如果解析失败，不报错
    - 而是返回空值 `NaT`

- `if not pd.isna(parsed):`
  - 如果成功解析出了日期

- `return parsed`
  - 就立刻返回这个日期结果

- `return pd.NaT`
  - 如果 3 种格式都解析失败
  - 那就返回空值

这段代码的核心作用是：

- 把混乱的日期格式统一识别出来

---

### 第 29-36 行：创建数据库连接

```python
def build_engine():
    password = quote_plus(DB_CONFIG["password"])
    url = (
        f"mysql+pymysql://{DB_CONFIG['user']}:{password}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        f"?charset={DB_CONFIG['charset']}"
    )
    return create_engine(url)
```

解释：

- `def build_engine():`
  - 定义一个函数，用来生成 MySQL 连接引擎

- `password = quote_plus(DB_CONFIG["password"])`
  - 先把密码做 URL 编码
  - 避免密码里有特殊符号导致连接字符串解析错误

- `url = (...)`
  - 拼出 MySQL 连接地址
  - 格式类似：

```text
mysql+pymysql://用户名:密码@主机:端口/数据库?charset=utf8mb4
```

- `return create_engine(url)`
  - 用 SQLAlchemy 创建连接引擎
  - 后面所有数据库操作都会通过这个引擎完成

---

### 第 39-55 行：数据清洗核心函数

```python
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_df = df.copy()

    cleaned_df["order_date"] = cleaned_df["order_date"].apply(parse_mixed_date)
    cleaned_df["amount"] = pd.to_numeric(cleaned_df["amount"], errors="coerce").round(2)
    cleaned_df["user_name"] = cleaned_df["user_name"].astype(str).str[:8]
    cleaned_df["remark"] = cleaned_df["remark"].astype(str).str[:20]
    cleaned_df["city"] = cleaned_df["city"].astype(str).str[:50]

    cleaned_df = cleaned_df.dropna(subset=["order_date", "amount"])
    cleaned_df["order_date"] = cleaned_df["order_date"].dt.date

    cleaned_df = cleaned_df.drop_duplicates(
        subset=["order_id", "user_name", "order_date"]
    ).reset_index(drop=True)

    return cleaned_df
```

解释：

- `def transform_data(df: pd.DataFrame) -> pd.DataFrame:`
  - 定义一个函数
  - 输入：原始表格
  - 输出：清洗后的表格

- `cleaned_df = df.copy()`
  - 复制一份原始数据
  - 这样后续修改不会影响原始 `df`

#### 日期处理

- `cleaned_df["order_date"] = cleaned_df["order_date"].apply(parse_mixed_date)`
  - 对 `order_date` 列的每一个值，都执行 `parse_mixed_date()`
  - 作用是统一处理混合日期格式

#### 金额处理

- `cleaned_df["amount"] = pd.to_numeric(cleaned_df["amount"], errors="coerce").round(2)`
  - `pd.to_numeric(...)`：把金额转成数字
  - 如果遇到非法值，用空值代替
  - `.round(2)`：保留两位小数

#### 字符串截取

- `cleaned_df["user_name"] = cleaned_df["user_name"].astype(str).str[:8]`
  - 先把用户名转成字符串
  - 再截取前 8 个字符

- `cleaned_df["remark"] = cleaned_df["remark"].astype(str).str[:20]`
  - 备注截取前 20 个字符

- `cleaned_df["city"] = cleaned_df["city"].astype(str).str[:50]`
  - 城市字段最多保留前 50 个字符
  - 这样能和数据库字段长度对齐

#### 删除空值

- `cleaned_df = cleaned_df.dropna(subset=["order_date", "amount"])`
  - 如果 `order_date` 或 `amount` 是空值，就删掉这一行
  - 因为这两个字段是入库时的关键字段

#### 日期类型再处理

- `cleaned_df["order_date"] = cleaned_df["order_date"].dt.date`
  - 把 Pandas 的日期时间，转成纯日期
  - 例如：只保留 `2024-01-15`
  - 不要时间部分

#### 去重

- `cleaned_df = cleaned_df.drop_duplicates(...)`
  - 按 `order_id + user_name + order_date` 组合去重

- `.reset_index(drop=True)`
  - 去重后重新整理行号
  - `drop=True` 表示旧行号不要保留

- `return cleaned_df`
  - 返回清洗后的结果

这段函数就是整个 ETL 的核心。

---

### 第 58-74 行：重建 MySQL 表

```python
def recreate_table(engine) -> None:
    table_name = DB_CONFIG["table_name"]
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        order_id INT NOT NULL,
        user_name VARCHAR(8) NOT NULL,
        order_date DATE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        city VARCHAR(50),
        remark VARCHAR(20),
        PRIMARY KEY (order_id, user_name, order_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    with engine.begin() as connection:
        connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        connection.execute(text(create_sql))
```

解释：

- `def recreate_table(engine) -> None:`
  - 定义一个函数，用来重建目标表

- `table_name = DB_CONFIG["table_name"]`
  - 从配置中取出表名

- `create_sql = f"""..."""`
  - 拼出建表 SQL

字段含义：

- `order_id INT NOT NULL`
  - 订单号，不能为空

- `user_name VARCHAR(8) NOT NULL`
  - 用户名最多 8 个字符

- `order_date DATE NOT NULL`
  - 日期字段

- `amount DECIMAL(10,2) NOT NULL`
  - 金额，保留两位小数

- `city VARCHAR(50)`
  - 城市

- `remark VARCHAR(20)`
  - 备注最多 20 个字符

- `PRIMARY KEY (order_id, user_name, order_date)`
  - 用三个字段组合作为主键
  - 这和你的去重规则是一致的

- `with engine.begin() as connection:`
  - 打开一个数据库连接，并自动开启事务

- `connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))`
  - 先删掉旧表

- `connection.execute(text(create_sql))`
  - 再创建新表

这一步的含义是：

- 这是一个“全量覆盖”的入库方案
- 每次执行 ETL，都先删表再重建再导入

---

### 第 77-87 行：把数据写入 MySQL

```python
def load_to_mysql(df: pd.DataFrame) -> None:
    engine = build_engine()
    recreate_table(engine)
    df.to_sql(
        DB_CONFIG["table_name"],
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )
```

解释：

- `def load_to_mysql(df: pd.DataFrame) -> None:`
  - 定义入库函数

- `engine = build_engine()`
  - 先创建数据库连接

- `recreate_table(engine)`
  - 重建目标表

- `df.to_sql(...)`
  - 把 DataFrame 直接写入数据库表

参数解释：

- `DB_CONFIG["table_name"]`
  - 目标表名

- `con=engine`
  - 使用哪个数据库连接

- `if_exists="append"`
  - 如果表已存在，就往里追加数据
  - 但因为前面已经删表重建了，所以这里本质上是插入新数据

- `index=False`
  - 不把 DataFrame 的行号写进数据库

- `method="multi"`
  - 批量插入
  - 会比一条一条插入更高效

- `chunksize=500`
  - 每批写入 500 行
  - 避免一次性塞太多数据

---

### 第 90-114 行：主流程

```python
def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"未找到原始文件: {RAW_FILE}，请先执行 generate_data.py"
        )

    raw_df = pd.read_csv(RAW_FILE)
    cleaned_df = transform_data(raw_df)
    cleaned_df.to_csv(CLEAN_FILE, index=False, encoding="utf-8-sig")
    try:
        load_to_mysql(cleaned_df)
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "MySQL 入库失败。请检查数据库账号密码是否正确，"
            "以及该账号是否已授权当前主机访问目标库。"
        ) from exc

    print(f"raw rows: {len(raw_df)}")
    print(f"clean rows: {len(cleaned_df)}")
    print(f"clean file: {CLEAN_FILE}")
    print(
        "mysql target: "
        f"{DB_CONFIG['database']}.{DB_CONFIG['table_name']} "
        f"@ {DB_CONFIG['host']}:{DB_CONFIG['port']}"
    )
```

解释：

#### 先检查原始文件是否存在

- `if not RAW_FILE.exists():`
  - 如果原始文件不存在

- `raise FileNotFoundError(...)`
  - 就抛出文件不存在异常
  - 并提示你先执行 `generate_data.py`

#### 读取 CSV

- `raw_df = pd.read_csv(RAW_FILE)`
  - 用 Pandas 读取原始 CSV 文件
  - 得到一个 DataFrame

#### 执行数据清洗

- `cleaned_df = transform_data(raw_df)`
  - 调用清洗函数
  - 得到清洗后的数据

#### 保存清洗结果

- `cleaned_df.to_csv(CLEAN_FILE, index=False, encoding="utf-8-sig")`
  - 把清洗结果另存为 `clean_orders.csv`
  - 方便你查看和验证

#### 入库并处理异常

- `try:`
  - 尝试执行入库

- `load_to_mysql(cleaned_df)`
  - 把清洗后的数据写入 MySQL

- `except SQLAlchemyError as exc:`
  - 如果数据库连接或执行 SQL 时出错

- `raise RuntimeError(...) from exc`
  - 抛出一个更容易看懂的错误提示
  - 告诉你重点检查：
    - 账号密码
    - 主机访问权限

#### 打印结果

- `print(f"raw rows: {len(raw_df)}")`
  - 打印原始数据行数

- `print(f"clean rows: {len(cleaned_df)}")`
  - 打印清洗后的行数

- `print(f"clean file: {CLEAN_FILE}")`
  - 打印清洗文件位置

- 最后一段 `print(...)`
  - 打印 MySQL 目标库和表信息

---

### 第 117-118 行：程序入口

```python
if __name__ == "__main__":
    main()
```

解释：

- 这是一句固定写法
- 表示：如果当前文件是被直接运行的，就执行 `main()`

也就是说，你直接运行：

```python
python etl_to_db.py
```

程序就会从这里开始执行

---

## 3. 这个脚本的执行流程

你可以把它简化理解为下面这条链路：

1. 先看 `raw_orders.csv` 在不在
2. 如果在，就读取 CSV
3. 对日期、金额、字符串做清洗
4. 删除空值
5. 按主键规则去重
6. 导出 `clean_orders.csv`
7. 连接 MySQL
8. 删除旧表并重建新表
9. 把清洗后的数据分批写入数据库

---

## 4. 你当前最需要记住的 Pandas 方法

先记住这几个最重要：

- `pd.read_csv(...)`
  - 读取 CSV 文件

- `df.copy()`
  - 复制一份表格数据

- `apply(...)`
  - 对一列的每个值执行同一个函数

- `pd.to_numeric(...)`
  - 把字段转成数字

- `.round(2)`
  - 保留两位小数

- `.astype(str)`
  - 转成字符串

- `.str[:8]`
  - 截取字符串前 8 位

- `dropna(...)`
  - 删除空值行

- `drop_duplicates(...)`
  - 去重

- `to_csv(...)`
  - 导出 CSV

- `to_sql(...)`
  - 导入数据库

---

## 5. 这份代码里最关键的 3 个函数

如果你只抓主线，先盯住这 3 个：

### `parse_mixed_date()`

作用：

- 把不同格式的日期统一解析出来

### `transform_data()`

作用：

- 做真正的数据清洗
- 包含日期、金额、字符串、空值、去重

### `load_to_mysql()`

作用：

- 把清洗结果写到 MySQL

---

## 6. 你学习这个文件的推荐顺序

建议你这样看：

第一遍：

- 只看 `main()`
- 明白整个 ETL 的执行流程

第二遍：

- 重点看 `transform_data()`
- 这是 Pandas 学习的核心

第三遍：

- 再看 `build_engine()` 和 `load_to_mysql()`
- 理解 Python 是怎么把数据写到 MySQL 里的

第四遍：

- 最后看 `recreate_table()`
- 理解全量覆盖导入的思路

---

## 7. 和你这个练习项目的关系

这份 `etl_to_db.py` 正好覆盖了你最开始提到的需求：

- 读取文件
- 日期格式转换
- 浮点数保留
- 字符串长度截取
- 去重
- 入库 MySQL

所以只要你把这个文件慢慢吃透，你这次 Pandas 练习的主干就已经抓住了。
