# contract_number.py
import json
from datetime import datetime
from pathlib import Path

COUNTER_FILE = Path("data/counter.json")


def load_counters():
    """
    Загружает счётчики из файла.
    Если файла нет или он пустой → возвращает пустой dict.
    """
    if not COUNTER_FILE.exists() or COUNTER_FILE.stat().st_size == 0:
        return {}
    try:
        return json.loads(COUNTER_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_counters(counters: dict):
    """
    Сохраняет счётчики в JSON.
    """
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    COUNTER_FILE.write_text(json.dumps(counters, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_contract_number(contract_date: datetime) -> str:
    """
    Формат номера договора:
    X/YY/MM/DD

    где:
      X = порядковый номер договора в день (1, 2, 3 …)
      YY = последние 2 цифры года
      MM = месяц
      DD = день
    """
    counters = load_counters()
    date_key = contract_date.strftime("%Y-%m-%d")

    current_count = counters.get(date_key, 0) + 1
    counters[date_key] = current_count
    save_counters(counters)

    # возвращаем строку с тире и слэшами → X-YY/MM/DD
    return f"{current_count}-{contract_date.strftime('%y/%m/%d')}"