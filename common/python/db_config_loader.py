from pathlib import Path
from configparser import ConfigParser

ROOT = Path(__file__).resolve().parents[2]  # 指向 big-data-skills 根
CONFIG_FILE = ROOT / "config" / "db_config.ini"

# 从配置文件加载数据库连接信息
# section: 数据库环境，如 dev、test、prod 等
    # 返回值: 包含数据库连接信息的字典
    # 包含 host、port、database、user、password 等键值对   
def load_db_config(section: str = "dev") -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"未找到数据库配置文件: {CONFIG_FILE}")

    parser = ConfigParser()
    parser.read(CONFIG_FILE, encoding="utf-8")

    if not parser.has_section(section):
        raise ValueError(f"配置文件中不存在 section: {section}")

    cfg = dict(parser.items("default"))
    cfg.update(dict(parser.items(section)))

    cfg["port"] = int(cfg["port"])
    return cfg

if __name__ == "__main__":
    print(load_db_config())