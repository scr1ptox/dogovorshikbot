# utils.py
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
<<<<<<< HEAD
import math


def round_up_amount(value: float) -> int:
    """Округляем всегда вверх до целого рубля."""
    return math.ceil(value)
=======
from decimal import Decimal, ROUND_UP


def round_up_amount(value) -> int:
    """
    Округляем всегда вверх до целого рубля.
    Принимает int | float | Decimal.
    """
    d = Decimal(str(value))
    return int(d.to_integral_value(rounding=ROUND_UP))
>>>>>>> 03ccfeb (Fix docx generation, disable PDF, stabilize template formatting)


def add_months_with_payday(base_date: datetime, months: int, payday: int) -> datetime:
    """
    Смещаем дату на `months` месяцев вперёд.
    Если в месяце нет нужного дня (например, 31),
    то ставим последний день месяца.
    """
    target = base_date + relativedelta(months=+months)
    days_in_month = (target + relativedelta(months=+1, day=1) - timedelta(days=1)).day
    return target.replace(day=min(payday, days_in_month))


def generate_schedule(start_date: datetime, term: int, payday: int, cost: int, advance: int):
    """
    Строим график платежей.
    - Первый платёж через месяц от даты договора.
    - Если в месяце нет 31 — сдвигаем на конец месяца.
    - Сумма делится равномерно (округление вверх).
    """
    balance = cost - advance
    if balance < 0:
        balance = 0

    # ежемесячный платёж с округлением вверх
<<<<<<< HEAD
    base_payment = math.ceil(balance / term)
=======
    base_payment = round_up_amount(Decimal(balance) / Decimal(term))
>>>>>>> 03ccfeb (Fix docx generation, disable PDF, stabilize template formatting)

    schedule = []
    current_date = start_date

    for i in range(term):
        current_date = add_months_with_payday(current_date, 1, payday)
        payment = min(base_payment, balance)
        balance -= payment
        schedule.append({
            "date": current_date.strftime("%d.%m.%Y"),
            "amount": payment,
            "balance": balance,
        })

    return schedule