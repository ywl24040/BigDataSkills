# `generate_data.py` 逐行学习笔记

对应源码文件：

- [generate_data.py](file:///g:/DataSkills/big-data-skills/Python_Pandas/ETL_DEMO1_FULL_LOAD/generate_data.py)

## 1. 这个脚本是做什么的

这个脚本的目标很简单：

1. 随机生成一批订单数据
2. 故意复制一部分数据，制造重复记录
3. 把结果保存成 `raw_orders.csv`

你可以把它理解成：

- 先造一份原始数据
- 再把这份原始数据交给后面的 ETL 脚本去清洗和入库

---

## 2. 源码逐段解释

### 第 1-5 行：导入模块

```python
from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd
```

解释：

- `from pathlib import Path`
  - 导入 `Path`
  - 它专门用来处理文件路径
  - 比如后面会用它找到当前脚本目录，再拼接出 `raw_orders.csv`

- `import random`
  - 导入随机数模块
  - 后面生成订单号、金额、城市、日期格式时都要用到它

- `from datetime import datetime, timedelta`
  - `datetime` 用来表示日期时间
  - `timedelta` 用来表示时间差，比如“加 10 天”

- `import pandas as pd`
  - 导入 `pandas`
  - `as pd` 是给它起一个简写名字
  - 以后看到 `pd.DataFrame(...)`，就知道是在调用 `pandas`

---

### 第 8-12 行：定义固定配置

```python
BASE_DIR = Path(__file__).resolve().parent
RAW_FILE = BASE_DIR / "raw_orders.csv"
TOTAL_ROWS = 3500
DUPLICATE_ROWS = 300
RANDOM_SEED = 20260818
```

解释：

- `BASE_DIR = Path(__file__).resolve().parent`
  - `__file__` 表示当前这个 Python 文件
  - `.resolve()` 表示拿到完整路径
  - `.parent` 表示所在文件夹
  - 所以 `BASE_DIR` 就是 `generate_data.py` 所在目录

- `RAW_FILE = BASE_DIR / "raw_orders.csv"`
  - 在当前目录下拼出一个文件路径
  - 这里的 `/` 不是除法，而是 `Path` 的路径拼接写法

- `TOTAL_ROWS = 3500`
  - 先生成 3500 行基础数据

- `DUPLICATE_ROWS = 300`
  - 再额外制造 300 行重复数据

- `RANDOM_SEED = 20260818`
  - 随机种子
  - 它的作用是让每次生成结果更稳定，便于学习和调试

---

### 第 15-21 行：把日期转换成不同格式的字符串

```python
def build_date_text(date_value: datetime) -> str:
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
    ]
    return date_value.strftime(random.choice(formats))
```

解释：

- `def build_date_text(date_value: datetime) -> str:`
  - `def` 是定义函数
  - 函数名叫 `build_date_text`
  - `date_value: datetime` 表示传入的参数是日期对象
  - `-> str` 表示这个函数返回的是字符串

- `formats = [...]`
  - 定义了 3 种日期格式：
    - `%Y-%m-%d` -> `2024-01-15`
    - `%Y/%m/%d` -> `2024/01/15`
    - `%d-%m-%Y` -> `15-01-2024`

- `return date_value.strftime(random.choice(formats))`
  - `random.choice(formats)`：从 3 种日期格式里随机选 1 种
  - `date_value.strftime(...)`：把日期对象按指定格式转成字符串

这一行的意义是：

- 故意让原始数据中的日期格式不统一
- 这样后面的 ETL 才有“日期格式转换”的练习价值

---

### 第 24-43 行：生成基础订单数据

```python
def build_base_rows(total_rows: int) -> list[dict]:
    random.seed(RANDOM_SEED)
    cities = ["Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Hangzhou", "Chengdu"]
    base_date = datetime(2024, 1, 1)
    rows = []

    for _ in range(total_rows):
        date_value = base_date + timedelta(days=random.randint(0, 365))
        rows.append(
            {
                "order_id": random.randint(10000, 12000),
                "user_name": f"user_{random.randint(1, 800):04d}_long_name",
                "order_date": build_date_text(date_value),
                "amount": round(random.uniform(50, 5000), 4),
                "city": random.choice(cities),
                "remark": f"sample_remark_for_etl_demo_{random.randint(100, 999)}",
            }
        )

    return rows
```

解释：

- `def build_base_rows(total_rows: int) -> list[dict]:`
  - 定义一个函数，用来生成很多条订单数据
  - `list[dict]` 的意思是：返回值是“由多个字典组成的列表”

- `random.seed(RANDOM_SEED)`
  - 设置随机种子
  - 让每次运行时生成的数据更可控

- `cities = [...]`
  - 定义一个城市列表
  - 后面会随机从里面选城市

- `base_date = datetime(2024, 1, 1)`
  - 定义起始日期为 `2024-01-01`

- `rows = []`
  - 先创建一个空列表，用来保存所有生成的数据

- `for _ in range(total_rows):`
  - 循环 `total_rows` 次
  - `_` 表示这个循环变量本身不重要，只是为了循环

- `date_value = base_date + timedelta(days=random.randint(0, 365))`
  - 从 `2024-01-01` 开始，随机加上 0 到 365 天
  - 这样就得到一个随机日期

- `rows.append({...})`
  - 往列表里追加一条订单记录
  - 每条记录是一个字典

字段解释：

- `"order_id": random.randint(10000, 12000)`
  - 随机生成订单编号

- `"user_name": f"user_{random.randint(1, 800):04d}_long_name"`
  - 生成用户名
  - `f"..."`
    是 Python 的格式化字符串写法
  - `:04d`
    的意思是：如果数字不够 4 位，就前面补 0
  - 比如 `7` 会变成 `0007`
  - 所以结果可能是：`user_0007_long_name`

- `"order_date": build_date_text(date_value)`
  - 调用前面那个函数，把日期变成随机格式的字符串

- `"amount": round(random.uniform(50, 5000), 4)`
  - `random.uniform(50, 5000)`：随机生成 50 到 5000 之间的小数
  - `round(..., 4)`：保留 4 位小数
  - 这里故意保留 4 位，是为了让后面的 ETL 脚本练习“保留 2 位小数”

- `"city": random.choice(cities)`
  - 从城市列表中随机选一个城市

- `"remark": f"sample_remark_for_etl_demo_{random.randint(100, 999)}"`
  - 随机生成一段备注文本
  - 后面可以拿它练习字符串截取

- `return rows`
  - 把生成好的所有数据返回出去

---

### 第 46-48 行：制造重复数据

```python
def append_duplicate_rows(rows: list[dict], duplicate_rows: int) -> list[dict]:
    sampled_rows = random.sample(rows, duplicate_rows)
    return rows + [row.copy() for row in sampled_rows]
```

解释：

- `def append_duplicate_rows(rows: list[dict], duplicate_rows: int) -> list[dict]:`
  - 定义一个函数
  - 作用是：在已有数据里再复制一部分数据，制造重复记录

- `sampled_rows = random.sample(rows, duplicate_rows)`
  - 从原来的数据中随机抽取 `duplicate_rows` 条记录

- `return rows + [row.copy() for row in sampled_rows]`
  - 原始数据 `rows`
  - 加上复制出来的重复数据
  - 拼接后一起返回

- `row.copy()`
  - 表示复制一份字典
  - 避免多个位置引用同一个对象

这一段的目的就是：

- 故意做出重复数据
- 方便后续练习 `drop_duplicates()`

---

### 第 51-59 行：主执行流程

```python
def main() -> None:
    rows = build_base_rows(TOTAL_ROWS)
    all_rows = append_duplicate_rows(rows, DUPLICATE_ROWS)
    df = pd.DataFrame(all_rows)
    df.to_csv(RAW_FILE, index=False, encoding="utf-8-sig")

    print(f"raw file: {RAW_FILE}")
    print(f"total rows written: {len(df)}")
    print(f"expected duplicates mixed in: {DUPLICATE_ROWS}")
```

解释：

- `def main() -> None:`
  - 定义主函数
  - 程序主要流程都写在这里

- `rows = build_base_rows(TOTAL_ROWS)`
  - 先生成 3500 行基础数据

- `all_rows = append_duplicate_rows(rows, DUPLICATE_ROWS)`
  - 再额外追加 300 行重复记录

- `df = pd.DataFrame(all_rows)`
  - 把 Python 列表数据转成 Pandas 的表格对象 `DataFrame`
  - 你可以先把它理解为“类似 Excel 表格的数据结构”

- `df.to_csv(RAW_FILE, index=False, encoding="utf-8-sig")`
  - 把 DataFrame 保存成 CSV 文件
  - `RAW_FILE` 表示保存位置
  - `index=False` 表示不要把行号写入 CSV
  - `encoding="utf-8-sig"` 是为了让文件在 Excel 中打开更稳定

- `print(...)`
  - 打印运行结果提示
  - 让你知道文件保存到了哪里、总共写入了多少行

---

### 第 62-63 行：程序入口

```python
if __name__ == "__main__":
    main()
```

解释：

- `if __name__ == "__main__":`
  - 你现在先把它理解成一句固定写法就行
  - 意思是：如果这个文件是被直接运行的，就执行下面的代码

- `main()`
  - 调用主函数
  - 程序就从这里开始正式运行

---

## 3. 运行流程总结

这个脚本真正执行时，流程如下：

1. 先读取脚本所在目录和输出文件路径
2. 生成 3500 条基础订单数据
3. 再复制 300 条数据作为重复记录
4. 把所有数据转成 Pandas DataFrame
5. 保存成 `raw_orders.csv`
6. 打印结果提示

---

## 4. 你当前最需要记住的语法

如果你现在刚开始学，先记住这几个就够了：

- `import`
  - 导入模块

- `def`
  - 定义函数

- `for`
  - 循环

- `list`
  - 列表

- `dict`
  - 字典

- `pd.DataFrame(...)`
  - 把数据变成表格

- `to_csv(...)`
  - 把表格保存成 CSV 文件

---

## 5. 建议你现在这样学习

第一遍：

- 先只看整体流程
- 知道这个脚本是“造数并导出文件”

第二遍：

- 重点看 `build_base_rows()`
- 理解每一行订单数据是怎么拼出来的

第三遍：

- 再看 `main()`
- 搞清楚数据是怎么一步一步写成 CSV 的

---

## 6. 下一步建议

等你看懂这个文件后，接下来最适合继续学的是：

- `etl_to_db.py`

因为它会带你接触：

- `read_csv()`
- 日期转换
- 金额保留小数
- 字符串截取
- 去重
- 写入 MySQL

这正好就是你这次练习项目的核心内容。
