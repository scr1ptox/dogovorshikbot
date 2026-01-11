# handlers.py
from datetime import datetime
<<<<<<< HEAD
from pathlib import Path
=======
>>>>>>> 03ccfeb (Fix docx generation, disable PDF, stabilize template formatting)
import os
import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler, ContextTypes, filters
)

from contract_number import generate_contract_number
from utils import generate_schedule, round_up_amount
from docx_generator import generate_contract_and_schedule
<<<<<<< HEAD

OUTPUT_DIR = Path("output") / "ready_contracts"
=======
from paths import OUTPUT_DIR
>>>>>>> 03ccfeb (Fix docx generation, disable PDF, stabilize template formatting)

# Conversation states
(
    CHOOSE_CONTRACT,
    DATE_CONTRACT,
    FIO_SELLER,
    FIO_BUYER,
    PHONE_BUYER,
    FIO_GUARANTOR,
    PHONE_GUARANTOR,
    ITEM_DESC,
    ITEM_QTY,
    PRIME_COST,
    MARKUP,
    ADVANCE,
    TERM_MONTHS,
    PAYDAY,
    PLEDGE,
    CONFIRM,
) = range(16)


# /start
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    logging.info("START -> CHOOSE_CONTRACT")
    kb = ReplyKeyboardMarkup([["Мурабаха"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Выберите договор:", reply_markup=kb)
    return CHOOSE_CONTRACT


async def choose_contract(update: Update, _: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    logging.info("CHOOSE_CONTRACT received: %r", text)
    if "мурабах" not in text:
        await update.message.reply_text("Пока доступен только «Мурабаха». Нажмите кнопку или введите 'Мурабаха'.")
        return CHOOSE_CONTRACT

    await update.message.reply_text(
        "Введите дату заключения договора (ДД.ММ.ГГГГ):",
        reply_markup=ReplyKeyboardRemove(),
    )
    logging.info("CHOOSE_CONTRACT -> DATE_CONTRACT")
    return DATE_CONTRACT


async def ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        dt = datetime.strptime(update.message.text.strip(), "%d.%m.%Y")
    except ValueError:
        await update.message.reply_text("Неверный формат. Введите дату как ДД.ММ.ГГГГ:")
        return DATE_CONTRACT

    context.user_data["data_dogovora_dt"] = dt
    context.user_data["data_dogovora"] = dt.strftime("%d.%m.%Y")
    context.user_data["contract_number"] = generate_contract_number(dt)  # X-YY_MM_DD

    await update.message.reply_text("Введите ФИО продавца:")
    return FIO_SELLER


async def ask_fio_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio_prodavca"] = update.message.text.strip()
    await update.message.reply_text("Введите ФИО покупателя:")
    return FIO_BUYER


async def ask_fio_buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio_pokupatelya"] = update.message.text.strip()
    await update.message.reply_text("Введите номер телефона покупателя:")
    return PHONE_BUYER


async def ask_phone_buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tel_pokupatelya"] = update.message.text.strip()
    await update.message.reply_text("Введите ФИО поручителя:")
    return FIO_GUARANTOR


async def ask_fio_guarantor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio_poruchitelya1"] = update.message.text.strip()
    await update.message.reply_text("Введите номер телефона поручителя:")
    return PHONE_GUARANTOR


async def ask_phone_guarantor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tel_poruchit1"] = update.message.text.strip()
    await update.message.reply_text("Введите полное описание товара:")
    return ITEM_DESC


async def ask_item_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pokupaemy_tov"] = update.message.text.strip()
    await update.message.reply_text("Введите количество товара (целое число):")
    return ITEM_QTY


async def ask_item_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = update.message.text.strip()
    if not s.isdigit() or int(s) <= 0:
        await update.message.reply_text("Количество должно быть положительным целым. Повторите:")
        return ITEM_QTY
    context.user_data["kolichestvo_tov"] = int(s)
    await update.message.reply_text("Введите себестоимость товара (рубли):")
    return PRIME_COST


async def ask_prime_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        val = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("Введите число (рубли). Повторите:")
        return PRIME_COST
    context.user_data["sebestoimost_tovara"] = round_up_amount(val)
    await update.message.reply_text("Введите наценку (рубли):")
    return MARKUP


async def ask_markup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        val = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("Введите число (рубли). Повторите:")
        return MARKUP
    context.user_data["nacenka_tov"] = round_up_amount(val)
    await update.message.reply_text("Введите первоначальный взнос (если нет — 0):")
    return ADVANCE


async def ask_advance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        val = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("Введите число (рубли). Повторите:")
        return ADVANCE
    context.user_data["pervi_vznos"] = round_up_amount(val)
    await update.message.reply_text("Введите срок договора (в месяцах):")
    return TERM_MONTHS


async def ask_term_months(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = update.message.text.strip()
    if not s.isdigit() or int(s) <= 0:
        await update.message.reply_text("Срок должен быть положительным целым. Повторите:")
        return TERM_MONTHS
    context.user_data["srok_dogov"] = int(s)
    await update.message.reply_text("Введите день месяца для оплаты (1–31):")
    return PAYDAY


async def ask_payday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = update.message.text.strip()
    if not s.isdigit():
        await update.message.reply_text("Введите число 1–31:")
        return PAYDAY
    d = int(s)
    if d < 1 or d > 31:
        await update.message.reply_text("День оплаты должен быть 1–31. Повторите:")
        return PAYDAY
    context.user_data["data_opl"] = d

    kb = ReplyKeyboardMarkup([["Да", "Нет"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Залог (Да/Нет)?", reply_markup=kb)
    return PLEDGE


async def ask_pledge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = update.message.text.strip().capitalize()
    if ans not in ("Да", "Нет"):
        await update.message.reply_text("Ответьте: Да или Нет")
        return PLEDGE
    context.user_data["zalog"] = ans

<<<<<<< HEAD
    await update.message.reply_text("Формирую документы...", reply_markup=ReplyKeyboardRemove())
    return await confirm_and_generate(update, context)
=======
    return await ask_confirm(update, context)


async def ask_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data

    qty = int(ud.get("kolichestvo_tov", 1))
    total_sebestoim = ud["sebestoimost_tovara"] * qty
    total_nacenka = ud["nacenka_tov"] * qty
    polnaya = total_sebestoim + total_nacenka

    text = (
        "Проверьте данные:\n\n"
        f"Договор: Мурабаха\n"
        f"Номер: {ud['contract_number']}\n"
        f"Дата: {ud['data_dogovora']}\n\n"
        f"Покупатель: {ud['fio_pokupatelya']}\n"
        f"Телефон: {ud['tel_pokupatelya']}\n\n"
        f"Товар: {ud['pokupaemy_tov']}\n"
        f"Количество: {qty}\n"
        f"Полная стоимость: {polnaya} руб.\n"
        f"Первый взнос: {ud['pervi_vznos']} руб.\n"
        f"Срок: {ud['srok_dogov']} мес.\n"
        f"День оплаты: {ud['data_opl']}\n"
        f"Залог: {ud['zalog']}\n"
    )

    kb = ReplyKeyboardMarkup(
        [["✅ Сгенерировать", "✏️ Исправить"], ["⛔️ Отмена"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(text, reply_markup=kb)
    return CONFIRM


async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip()

    if txt.startswith("✅"):
        await update.message.reply_text("Формирую документы...", reply_markup=ReplyKeyboardRemove())
        return await confirm_and_generate(update, context)

    if txt.startswith("✏️"):
        await update.message.reply_text(
            "Начнём заново. Введите дату договора (ДД.ММ.ГГГГ):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return DATE_CONTRACT

    if txt.startswith("⛔"):
        context.user_data.clear()
        kb = ReplyKeyboardMarkup([["Мурабаха"]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Отменено. Выберите договор:", reply_markup=kb)
        return CHOOSE_CONTRACT

    await update.message.reply_text("Выберите действие кнопками.")
    return CONFIRM
>>>>>>> 03ccfeb (Fix docx generation, disable PDF, stabilize template formatting)


async def confirm_and_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data

    # суммы по ТЗ (учитываем количество)
    qty = int(ud.get("kolichestvo_tov", 1))
    total_sebestoim = ud["sebestoimost_tovara"] * qty
    total_nacenka = ud["nacenka_tov"] * qty
    polnaya_stoimost = total_sebestoim + total_nacenka
    ostatok_dolga = max(0, polnaya_stoimost - ud["pervi_vznos"])

    # график
    schedule = generate_schedule(
        start_date=ud["data_dogovora_dt"],
        term=ud["srok_dogov"],
        payday=ud["data_opl"],
        cost=polnaya_stoimost,
        advance=ud["pervi_vznos"],
    )
    ejemes = schedule[0]["amount"] if schedule else 0

    # Маппинг ПОД ПОЛНЫЕ ПЛЕЙСХОЛДЕРЫ (ключи с {{...}})
    repl = {
        "{{nomer_dogovora}}": ud["contract_number"],
        "{{data_dogovora}}": ud["data_dogovora"],
        "{{fio_prodavca}}": ud["fio_prodavca"],
        "{{fio_pokupatelya}}": ud["fio_pokupatelya"],
        "{{tel_pokupatelya}}": ud["tel_pokupatelya"],
        "{{fio_poruchitelya1}}": ud["fio_poruchitelya1"],
        "{{tel_poruchit1}}": ud["tel_poruchit1"],
        "{{pokupaemy_tov}}": ud["pokupaemy_tov"],
        "{{kolichestvo_tov}}": ud["kolichestvo_tov"],
        "{{polnaya_stoimost_tov}}": polnaya_stoimost,
        "{{sebestoimost_tovara}}": total_sebestoim,
        "{{nacenka_tov}}": total_nacenka,
        "{{pervi_vznos}}": ud["pervi_vznos"],
        "{{srok_dogov}}": ud["srok_dogov"],
        "{{ejemes_oplata}}": ejemes,
        "{{data_opl}}": ud["data_opl"],
        "{{zalog}}": ud["zalog"],

        # график (шапка)
        "{{ostatok_dolga}}": ostatok_dolga,
    }

    # 12 строк графика: заполняем по сроку, лишние — пустые
    for i in range(1, 13):
        if i <= len(schedule):
            row = schedule[i - 1]
            repl[f"{{{{data_plateja{i}}}}}"] = row["date"]
            repl[f"{{{{summa_plateja{i}}}}}"] = row["amount"]
            repl[f"{{{{ostatok_posle_plateja{i}}}}}"] = row["balance"]
        else:
            repl[f"{{{{data_plateja{i}}}}}"] = ""
            repl[f"{{{{summa_plateja{i}}}}}"] = ""
            repl[f"{{{{ostatok_posle_plateja{i}}}}}"] = ""

    # contract_number for replacements
    repl["contract_number"] = ud["contract_number"]
    # генерим .docx
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
<<<<<<< HEAD
    contract_path, schedule_path = generate_contract_and_schedule(
=======
    contract_docx, schedule_docx = generate_contract_and_schedule(
>>>>>>> 03ccfeb (Fix docx generation, disable PDF, stabilize template formatting)
        data=repl, out_dir=OUTPUT_DIR
    )

    # отправляем и чистим
    try:
<<<<<<< HEAD
        await update.message.reply_document(open(contract_path, "rb"), filename=contract_path.name)
        await update.message.reply_document(open(schedule_path, "rb"), filename=schedule_path.name)
    finally:
        for p in (contract_path, schedule_path):
=======
        for path in (contract_docx, schedule_docx):
            with open(path, "rb") as f:
                await update.message.reply_document(f, filename=path.name)
    finally:
        for p in (contract_docx, schedule_docx):
>>>>>>> 03ccfeb (Fix docx generation, disable PDF, stabilize template formatting)
            try:
                os.remove(p)
            except Exception:
                pass

    # очистим пользовательские данные и вернём меню выбора договора
    try:
        context.user_data.clear()
    except Exception:
        pass
    kb = ReplyKeyboardMarkup([["Мурабаха"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("✅ Готово. Хотите заполнить ещё один договор? Выберите:", reply_markup=kb)
    return CHOOSE_CONTRACT


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSE_CONTRACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_contract)],
        DATE_CONTRACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date)],
        FIO_SELLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_fio_seller)],
        FIO_BUYER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_fio_buyer)],
        PHONE_BUYER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone_buyer)],
        FIO_GUARANTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_fio_guarantor)],
        PHONE_GUARANTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone_guarantor)],
        ITEM_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_item_desc)],
        ITEM_QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_item_qty)],
        PRIME_COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_prime_cost)],
        MARKUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_markup)],
        ADVANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_advance)],
        TERM_MONTHS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_term_months)],
        PAYDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_payday)],
        PLEDGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_pledge)],
<<<<<<< HEAD
        CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_pledge)],
=======
        CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirm)],
>>>>>>> 03ccfeb (Fix docx generation, disable PDF, stabilize template formatting)
    },
    fallbacks=[CommandHandler("start", start)],
)