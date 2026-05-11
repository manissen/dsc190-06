from datetime import date

import pytest

from nldate import parse


TODAY = date(2025, 11, 20)


def test_today():
    assert parse("today", TODAY) == TODAY


def test_tomorrow():
    assert parse("tomorrow", TODAY) == date(2025, 11, 21)


def test_yesterday():
    assert parse("yesterday", TODAY) == date(2025, 11, 19)


def test_in_days():
    assert parse("in 3 days", TODAY) == date(2025, 11, 23)


def test_days_ago():
    assert parse("5 days ago", TODAY) == date(2025, 11, 15)


def test_next_tuesday():
    assert parse("next Tuesday", TODAY) == date(2025, 11, 25)


def test_last_tuesday():
    assert parse("last Tuesday", TODAY) == date(2025, 11, 18)


def test_month_day_year():
    assert parse("December 1st, 2025", TODAY) == date(2025, 12, 1)


def test_days_before_date():
    assert parse("5 days before December 1st, 2025", TODAY) == date(2025, 11, 26)


def test_year_and_month_after_yesterday():
    assert parse("1 year and 2 months after yesterday", TODAY) == date(2027, 1, 19)


def test_iso_format():
    assert parse("2025-12-01", TODAY) == date(2025, 12, 1)


def test_bad_input():
    with pytest.raises(ValueError):
        parse("not a date", TODAY)


def test_slash_date():
    assert parse("2025/12/04", TODAY) == date(2025, 12, 4)


def test_abbrev_month():
    assert parse("Dec 1, 2025", TODAY) == date(2025, 12, 1)


def test_abbrev_month_and_period():
    assert parse("Dec. 1, 2025", TODAY) == date(2025, 12, 1)


def test_two_units_comma_before_abbrev_date():
    assert parse("2 years, 3 months before Dec. 1, 2025", TODAY) == date(2023, 9, 1)


def test_day_after_tomorrow():
    assert parse("the day after tomorrow", TODAY) == date(2025, 11, 22)
