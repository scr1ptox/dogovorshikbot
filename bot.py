# bot.py
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram.constants import ParseMode
from telegram.ext import Application, Defaults

from handlers import conv_handler


PROJECT_ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "output" / "ready_contracts"
DATA_DIR = PROJECT_ROOT / "data"
COUNTER_FILE = DATA_DIR / "counter.json"


def ensure_project_layout() -> None:
    """
    Создаёт нужные директории/файлы, если их нет.
    Предупреждает, если нет шаблонов.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Инициализируем counter.json, если пусто/нет
    if not COUNTER_FILE.exists() or COUNTER_FILE.stat().st_size == 0:
        COUNTER_FILE.write_text("{}", encoding="utf-8")

    # Проверяем наличие шаблонов
    missing = []
    for name in ("murabaha_template.docx", "murabaha_schedule.docx"):
        if not (TEMPLATES_DIR / name).exists():
            missing.append(name)
    if missing:
        logging.warning("⚠️ Missing templates: %s (put them into %s)",
                        ", ".join(missing), TEMPLATES_DIR)


def setup_logging() -> None:
    """
    Настраивает лаконичное логирование.
    """
    log_fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # Уберём шум от httpx / PTB, оставим инфо-уровень
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram.vendor.ptb_urllib3.urllib3").setLevel(logging.WARNING)


async def on_startup(_: Application) -> None:
    logging.info("✅ dogovorshikbot started (polling)")


async def on_shutdown(_: Application) -> None:
    logging.info("🛑 dogovorshikbot stopped")


def main() -> None:
    load_dotenv()
    setup_logging()
    ensure_project_layout()

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Put it into .env or env vars.")

    # Парсим HTML по умолчанию (для жирного текста и т.п.)
    defaults = Defaults(parse_mode=ParseMode.HTML)

    app = Application.builder().token(token).defaults(defaults).build()

    # Хэндлер диалога (подключается один объект conv_handler)
    app.add_handler(conv_handler)

    # Хэндлер на ошибки — чтобы не падать молча
    async def error_handler(_, context):
        logging.exception("Unhandled error: %s", context.error)

    app.add_error_handler(error_handler)

    # Хуки старта/остановки
    app.post_init = on_startup
    app.post_stop = on_shutdown

    # Запуск
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()