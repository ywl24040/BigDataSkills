from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
FEED_FILES_DIR= BASE_DIR / "FeedFiles" 
RAW_FILE = FEED_FILES_DIR / "raw_orders.csv"      
CLEAN_FILE = FEED_FILES_DIR / "clean_orders.csv"
TOTAL_ROWS = 3500
DUPLICATE_ROWS = 300
RANDOM_SEED = 20260818


def build_date_text(date_value: datetime) -> str:
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
    ]
    #从 3 种日期格式里随机选 1 种
    selected_format = random.choice(formats)
    return date_value.strftime(selected_format)

# 生成基础订单数据
# 每个订单包含订单 ID、用户名称、订单日期、订单金额、城市、备注
#  list[dict]  每个 dict 包含订单 ID、用户名称、订单日期、订单金额、城市、备注
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


def append_duplicate_rows(rows: list[dict], duplicate_rows: int) -> list[dict]:
    sampled_rows = random.sample(rows, duplicate_rows)
    # return rows + [row.copy() for row in sampled_rows]
    return rows + sampled_rows


def main() -> None:
    rows = build_base_rows(TOTAL_ROWS)
    all_rows = append_duplicate_rows(rows, DUPLICATE_ROWS)
    df = pd.DataFrame(all_rows)
    df.to_csv(RAW_FILE, index=False, encoding="utf-8-sig",decimal=",",quotechar='"',quoting='all')

    print(f"raw file: {RAW_FILE}")
    print(f"total rows written: {len(df)}")
    print(f"expected duplicates mixed in: {DUPLICATE_ROWS}")


if __name__ == "__main__":
    main()
