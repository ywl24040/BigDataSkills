# Pandas ETL 入库练习项目需求

## 1. 项目简介

本项目用于练习 Python Pandas 的基础数据处理能力，围绕一个完整的小型 ETL 场景展开：

1. 使用 Pandas 模拟生成一份至少 3000 行的订单数据文件
2. 从文件中读取数据
3. 对数据进行清洗与转换
4. 将清洗后的结果写入数据库
5. 验证入库结果是否正确

本练习项目适合 Pandas 入门阶段，用来熟悉文件处理、字段转换、去重、入库等常见操作。

## 2. 项目目标

通过本项目，需要掌握以下内容：

- 使用 Pandas 生成模拟数据
- 将 DataFrame 保存为 CSV 文件
- 使用 Pandas 读取 CSV 文件
- 进行日期格式转换
- 对浮点型字段保留小数位
- 对字符串字段按长度进行截取
- 对重复数据进行去重
- 将清洗后的数据写入 MySQL 数据库

## 3. 技术栈建议

- Python 3.12
- Pandas
- MySQL
- `pymysql` 或 `SQLAlchemy + pymysql`

说明：

- 当前练习项目直接使用本地服务器上的 MySQL
- 后续代码实现时，建议优先使用 `SQLAlchemy + pymysql` 连接数据库

## 4. 业务场景说明

假设我们拿到了一份订单原始文件，原始数据存在以下问题：

- 日期格式不统一
- 金额字段小数位不规范
- 用户名和备注字段长度过长
- 文件中存在重复记录

因此需要编写一个 Pandas ETL 脚本，对数据进行规范化处理后再写入数据库。

## 5. 数据规模要求

- 原始数据文件行数不少于 3000 行
- 建议生成 3500 行左右数据，便于测试去重后的行数变化
- 数据中应主动混入部分重复记录，方便练习 `drop_duplicates`

## 6. 输入与输出

### 输入

- 原始文件：`raw_orders.csv`

### 输出

- 清洗后的数据表：`orders`
- MySQL 数据库中的 `orders` 表

可选输出：

- 清洗后的中间文件：`clean_orders.csv`

## 7. 建议目录结构

```text
big-data-skills/
└─ Python_Pandas/
   ├─ pandas_etl_practice_requirements.md
   ├─ generate_data.py
   ├─ etl_to_db.py
   ├─ raw_orders.csv
   ├─ clean_orders.csv
   └─ db_config_example.txt
```

## 8. 原始文件字段设计

建议模拟生成以下字段：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| order_id | int | 订单编号 |
| user_name | string | 用户名 |
| order_date | string | 订单日期，原始格式可混用多种写法 |
| amount | float | 订单金额 |
| city | string | 城市 |
| remark | string | 备注信息 |

## 9. 数据库表结构设计

数据库名称：`db_big_data`

表名：`orders`

| 字段名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| order_id | INT | 是 | 订单编号 |
| user_name | VARCHAR(8) | 是 | 截取后的用户名 |
| order_date | DATE | 是 | 统一转换后的日期，格式为 `YYYY-MM-DD` |
| amount | DECIMAL(10,2) | 是 | 保留两位小数后的金额 |
| city | VARCHAR(50) | 否 | 城市 |
| remark | VARCHAR(20) | 否 | 截取后的备注 |

## 10. MySQL 连接信息

当前环境使用以下数据库连接：

| 配置项 | 值 |
| --- | --- |
| Host | `192.168.5.20` |
| Port | `3306` |
| Username | `db_big_data` |
| Database | `db_big_data` |

说明：

- 密码不写入项目文档，后续代码实现时建议放到配置文件或环境变量中
- Python 连接时建议统一使用 UTF-8 编码
- 如果后续要做批量导入，可以继续补充连接池配置

参考建表语句如下：

```sql
CREATE TABLE orders (
    order_id INT NOT NULL,
    user_name VARCHAR(8) NOT NULL,
    order_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    city VARCHAR(50),
    remark VARCHAR(20),
    PRIMARY KEY (order_id, user_name, order_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 11. 数据处理规则

### 11.1 日期格式转换

目标：

- 将 `order_date` 统一转换为 `YYYY-MM-DD`

原始数据中可混入以下格式：

- `2024-01-15`
- `2024/01/15`
- `15-01-2024`

处理建议：

- 使用 `pd.to_datetime(..., errors="coerce")`
- 对无法解析的日期可转为缺失值，后续按需要选择删除或保留

### 11.2 浮点型保留

目标：

- 将 `amount` 字段统一保留两位小数

处理建议：

- 使用 `round(2)` 或等价方式

### 11.3 字符串长度截取

目标：

- `user_name` 截取前 8 个字符
- `remark` 截取前 20 个字符

处理建议：

- 使用 `astype(str).str[:8]`
- 使用 `astype(str).str[:20]`

### 11.4 去重规则

目标：

- 删除重复数据

建议去重键：

- `order_id`
- `user_name`
- `order_date`

处理建议：

- 使用 `drop_duplicates(subset=["order_id", "user_name", "order_date"])`

## 12. 项目功能拆分

建议拆成两个脚本：

### 12.1 数据生成脚本

文件名建议：`generate_data.py`

功能：

- 生成不少于 3000 行模拟数据
- 混入重复记录
- 保存为 `raw_orders.csv`

### 12.2 ETL 入库脚本

文件名建议：`etl_to_db.py`

功能：

- 读取 `raw_orders.csv`
- 完成日期格式转换
- 完成金额保留两位小数
- 完成字符串截取
- 完成去重
- 将结果写入 MySQL 的 `db_big_data.orders`

## 13. 验收标准

完成后应满足以下要求：

1. 能成功生成不少于 3000 行的原始数据文件
2. 能成功读取原始文件并生成 DataFrame
3. `order_date` 已统一转换为 `YYYY-MM-DD`
4. `amount` 已统一保留两位小数
5. `user_name` 和 `remark` 已完成截取
6. 重复数据已被删除
7. 清洗结果已成功写入 MySQL 数据库
8. 能使用 SQL 查询到入库后的数据

## 14. 建议扩展练习

完成基础版本后，可以继续追加以下练习：

- 增加空值处理
- 增加异常日期处理
- 将结果同时导出为 `clean_orders.csv`
- 编写 SQL 统计每天订单数量与总金额
- 增加分批写入 MySQL
- 增加唯一索引冲突处理

## 15. 下一步实施建议

推荐按以下顺序完成：

1. 先编写 `generate_data.py`，生成测试文件
2. 再编写 `etl_to_db.py`，完成读取、清洗和入库
3. 最后增加一个查询验证步骤，确认数据库结果正确

等这份需求确认后，就可以继续在当前目录中创建对应的 Python 脚本并开始实现。
