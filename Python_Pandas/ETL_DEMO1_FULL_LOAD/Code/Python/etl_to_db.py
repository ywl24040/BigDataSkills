from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from db_config import DB_CONFIG


BASE_DIR = Path(__file__).resolve().parent
RAW_FILE = BASE_DIR / "raw_orders.csv"
CLEAN_FILE = BASE_DIR / "clean_orders.csv"


def parse_mixed_date(value: object) -> pd.Timestamp:
    if pd.isna(value):
        return pd.NaT

    text_value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        parsed = pd.to_datetime(text_value, format=fmt, errors="coerce")
        if not pd.isna(parsed):
            return parsed

    return pd.NaT


def build_engine():
    password = quote_plus(DB_CONFIG["password"])
    url = (
        f"mysql+pymysql://{DB_CONFIG['user']}:{password}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        f"?charset={DB_CONFIG['charset']}"
    )
    return create_engine(url)


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


if __name__ == "__main__":
    main()
