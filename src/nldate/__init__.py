from __future__ import annotations

import re
from calendar import monthrange
from datetime import date, timedelta


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

NUM_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _clean(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", s)
    s = s.replace(",", "")
    return re.sub(r"\s+", " ", s)


def _num(s: str) -> int:
    if s.isdigit():
        return int(s)
    return NUM_WORDS[s]


def _add_months(d: date, months: int) -> date:
    total = d.month - 1 + months
    year = d.year + total // 12
    month = total % 12 + 1
    day = min(d.day, monthrange(year, month)[1])
    return date(year, month, day)


def _add(d: date, amount: int, unit: str) -> date:
    if unit.startswith("day"):
        return d + timedelta(days=amount)
    if unit.startswith("week"):
        return d + timedelta(weeks=amount)
    if unit.startswith("month"):
        return _add_months(d, amount)
    if unit.startswith("year"):
        return _add_months(d, amount * 12)
    raise ValueError(f"Unknown unit: {unit}")


def _parse_base(s: str, today: date) -> date:
    if s in {"today", "now"}:
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)

    m = re.fullmatch(r"next (" + "|".join(WEEKDAYS) + r")", s)
    if m:
        target = WEEKDAYS[m.group(1)]
        days = (target - today.weekday()) % 7
        if days == 0:
            days = 7
        return today + timedelta(days=days)

    m = re.fullmatch(r"last (" + "|".join(WEEKDAYS) + r")", s)
    if m:
        target = WEEKDAYS[m.group(1)]
        days = (today.weekday() - target) % 7
        if days == 0:
            days = 7
        return today - timedelta(days=days)

    m = re.fullmatch(r"(" + "|".join(WEEKDAYS) + r")", s)
    if m:
        target = WEEKDAYS[m.group(1)]
        days = (target - today.weekday()) % 7
        return today + timedelta(days=days)

    month_names = "|".join(MONTHS)

    m = re.fullmatch(rf"({month_names}) (\d{{1,2}}) (\d{{4}})", s)
    if m:
        return date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))

    m = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    raise ValueError(f"Could not parse date: {s}")


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = _clean(s)

    m = re.fullmatch(
        r"in (\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten) (day|days|week|weeks|month|months|year|years)",
        s,
    )
    if m:
        return _add(today, _num(m.group(1)), m.group(2))

    m = re.fullmatch(
        r"(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten) (day|days|week|weeks|month|months|year|years) ago",
        s,
    )
    if m:
        return _add(today, -_num(m.group(1)), m.group(2))

    m = re.fullmatch(
        r"(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten) "
        r"(day|days|week|weeks|month|months|year|years) "
        r"(before|after|from) (.+)",
        s,
    )
    if m:
        amount = _num(m.group(1))
        unit = m.group(2)
        direction = m.group(3)
        base = _parse_base(m.group(4), today)

        if direction == "before":
            amount *= -1

        return _add(base, amount, unit)

    m = re.fullmatch(
        r"(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten) "
        r"(year|years|month|months|week|weeks|day|days) and "
        r"(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten) "
        r"(year|years|month|months|week|weeks|day|days) "
        r"(before|after|from) (.+)",
        s,
    )
    if m:
        amount1 = _num(m.group(1))
        unit1 = m.group(2)
        amount2 = _num(m.group(3))
        unit2 = m.group(4)
        direction = m.group(5)
        base = _parse_base(m.group(6), today)

        sign = -1 if direction == "before" else 1
        result = _add(base, sign * amount1, unit1)
        result = _add(result, sign * amount2, unit2)
        return result

    return _parse_base(s, today)
