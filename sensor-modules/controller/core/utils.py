from pathlib import Path
from typing import Any
import re
import yaml


def load_config(path: str | Path) -> dict:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get_exchange_config(node_config: dict, 
                        exchanges: dict, 
                        config_key: str
) -> dict:
    exchange_key = node_config.get(config_key)
    if exchange_key is None:
        return {}
    return exchanges.get(exchange_key, {})

def get_exchange_name(node_config: dict, 
                      exchanges: dict, 
                      config_key: str
) -> str:
    exchange_cfg = get_exchange_config(node_config, exchanges, config_key)
    return exchange_cfg.get("name")

def dict_to_csv_line(fields: list[str], row: dict[str, Any]) -> str:
    values = [str(row.get(field, "")) for field in fields]
    return ",".join(values) + "\n"
