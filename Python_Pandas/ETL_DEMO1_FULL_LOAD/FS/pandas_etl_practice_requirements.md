# Pandas ETL Demo 1 全量入库练习

## 1. 项目目标

本项目用于练习一个完整的 Pandas ETL 全量入库流程：

1. 使用 Pandas 生成不少于 3000 行的模拟订单数据
2. 将模拟数据保存为 CSV 文件
3. 读取原始文件并进行数据清洗
4. 对日期、金额、字符串字段进行规范化处理
5. 对重复数据进行去重
6. 将清洗后的结果全量写入 MySQL 表

## 2. 技术栈

- Python 3.12
- pandas
- SQLAlchemy
- PyMySQL
- MySQL

## 3. 目录结构

```text
ETL_DEMO1_FULL_LOAD/
├─ pandas_etl_practice_requirements.md
├─ requirements.txt
├─ db_config.py
├─ generate_data.py
├─ etl_to_db.py
├─ raw_orders.csv
└─ clean_orders.csv
```

## 4. 数据规模要求

- 原始文件不少于 3000 行
- 建议生成约 3500 行基础数据
- 额外混入部分重复数据，便于练习去重

## 5. 原始数据字段

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| order_id | int | 订单编号 |
| user_name | string | 用户名，原始值允许较长 |
| order_date | string | 订单日期，混合多种格式 |
| amount | float | 订单金额 |
| city | string | 城市 |
| remark | string | 备注 |

## 6. 数据清洗规则

### 6.1 日期格式转换

- 将 `order_date` 统一转换为 `YYYY-MM-DD`
- 原始值允许混用以下格式：
  - `2024-01-15`
  - `2024/01/15`
  - `15-01-2024`

### 6.2 浮点型保留

- 将 `amount` 保留两位小数

### 6.3 字符串截取

- `user_name` 截取前 8 个字符
- `remark` 截取前 20 个字符

### 6.4 去重规则

- 按 `order_id + user_name + order_date` 组合去重

## 7. MySQL 连接信息

目标数据库：

- Host: `192.168.5.20`
- Port: `3306`
- Database: `db_big_data`
- Username: `db_big_data`

说明：

- 连接参数统一放在 `db_config.py`
- 该练习项目使用全量覆盖写入

## 8. 目标表结构

表名：`orders`

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

## 9. 脚本说明

### 9.1 `generate_data.py`

负责生成模拟原始文件：

- 生成基础订单数据
- 混入重复记录
- 输出 `raw_orders.csv`

### 9.2 `etl_to_db.py`

负责执行全量 ETL：

- 读取 `raw_orders.csv`
- 清洗和转换字段
- 去重
- 输出 `clean_orders.csv`
- 全量写入 MySQL 的 `orders` 表

## 10. 验收标准

完成后应满足以下条件：

1. 成功生成 `raw_orders.csv`
2. 原始文件数据量不少于 3000 行
3. 清洗后的日期格式统一
4. 金额字段保留两位小数
5. 字符串字段已按要求截取
6. 重复数据已被移除
7. 成功生成 `clean_orders.csv`
8. 成功写入 MySQL 表 `db_big_data.orders`
