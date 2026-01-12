# contract_number.py
import json
from datetime import datetime
from paths import COUNTER_FILE
import portalocker


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
    X-YY/MM/DD
    """
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)

    # открываем файл с блокировкой
    with open(COUNTER_FILE, "a+", encoding="utf-8") as f:
        portalocker.lock(f, portalocker.LOCK_EX)
        f.seek(0)

        try:
            data = f.read().strip()
            counters = json.loads(data) if data else {}
        except json.JSONDecodeError:
            counters = {}

        date_key = contract_date.strftime("%Y-%m-%d")
        current_count = counters.get(date_key, 0) + 1
        counters[date_key] = current_count

        f.seek(0)
        f.truncate()
        f.write(json.dumps(counters, ensure_ascii=False, indent=2))
        f.flush()

        portalocker.unlock(f)

    return f"{current_count}-{contract_date.strftime('%y/%m/%d')}"