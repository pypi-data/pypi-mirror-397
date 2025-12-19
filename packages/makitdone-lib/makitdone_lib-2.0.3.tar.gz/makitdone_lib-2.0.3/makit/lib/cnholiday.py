# coding:utf-8

from datetime import datetime

import arrow
from arrow import Arrow

from makit.lib.const import DEFAULT_DATE_FORMAT

workdays_cache = {}

# 法定节假日
LAW_HOLIDAYS = {
    2022: [
        (datetime(2022, 1, 1), datetime(2022, 1, 3)),  # 元旦
        (datetime(2022, 1, 31), datetime(2022, 2, 6)),  # 新年
        (datetime(2022, 4, 3), datetime(2022, 4, 5)),  # 清明
        (datetime(2022, 4, 30), datetime(2022, 5, 4)),  # 五一
        (datetime(2022, 6, 3), datetime(2022, 6, 5)),  # 端午
        (datetime(2022, 9, 10), datetime(2022, 9, 12)),  # 中秋
        (datetime(2022, 10, 1), datetime(2022, 10, 7))  # 国庆
    ],
    2023: [
        (datetime(2023, 1, 1), datetime(2023, 1, 2)),  # 元旦
        (datetime(2023, 1, 21), datetime(2023, 1, 27)),  # 新年
        (datetime(2023, 4, 5), datetime(2023, 4, 5)),  # 清明
        (datetime(2023, 4, 29), datetime(2023, 5, 3)),  # 五一
        (datetime(2023, 6, 22), datetime(2023, 6, 24)),  # 端午
        (datetime(2023, 9, 29), datetime(2023, 10, 6)),  # 中秋+国庆
        (datetime(2023, 12, 30), datetime(2023, 12, 31)),  # 元旦
    ],
    2024: [
        (datetime(2024, 1, 1), datetime(2024, 1, 1)),  # 元旦
        (datetime(2024, 2, 10), datetime(2024, 2, 17)),  # 新年
        (datetime(2024, 4, 4), datetime(2024, 4, 6)),  # 清明
        (datetime(2024, 5, 1), datetime(2024, 5, 5)),  # 五一
        (datetime(2024, 6, 8), datetime(2024, 6, 10)),  # 端午
        (datetime(2024, 9, 15), datetime(2024, 9, 17)),  # 中秋
        (datetime(2024, 10, 1), datetime(2024, 10, 7)),  # 国庆
    ],
    2025: [
        (datetime(2025, 1, 1), datetime(2025, 1, 1)),  # 元旦
        (datetime(2025, 1, 28), datetime(2025, 2, 4)),  # 新年
        (datetime(2025, 4, 4), datetime(2025, 4, 6)),  # 清明
        (datetime(2025, 5, 1), datetime(2025, 5, 5)),  # 五一
        (datetime(2025, 5, 31), datetime(2025, 6, 2)),  # 端午
        (datetime(2025, 10, 1), datetime(2025, 10, 8)),  # 国庆中秋
    ],
    2026: [
        (datetime(2026, 1, 1), datetime(2026, 1, 3)),  # 元旦
        (datetime(2026, 2, 15), datetime(2026, 2, 23)),  # 新年
        (datetime(2026, 4, 4), datetime(2026, 4, 6)),  # 清明
        (datetime(2026, 5, 1), datetime(2026, 5, 5)),  # 五一
        (datetime(2026, 6, 19), datetime(2026, 6, 21)),  # 端午
        (datetime(2026, 9, 25), datetime(2026, 9, 27)),  # 中秋
        (datetime(2026, 10, 1), datetime(2026, 10, 7)),  # 国庆
    ]
}

# 调班
ADJUST_WORKDAYS = {
    2022: [
        '2022-01-29', '2022-01-30', '2022-04-02', '2022-04-24', '2022-05-07',
        '2022-10-08', '2022-10-09'
    ],
    2023: [
        '2023-01-28', '2023-01-29', '2023-04-23', '2023-05-06', '2023-06-25',
        '2023-10-07', '2023-10-08'
    ],
    2024: [
        '2024-02-04', '2024-02-18', '2024-04-07', '2024-04-28', '2024-05-11',
        '2024-09-14', '2024-09-29', '2024-10-12'
    ],
    2025: [
        '2025-01-26', '2025-02-08', '2025-04-27', '2025-09-28', '2025-10-11',
    ],
    2026: [
        '2026-01-04', '2026-02-14', '2026-02-28', '2026-05-09', '2026-09-20',
        '2026-10-10',
    ]
}


def shift_dt(dt: datetime, **kwargs) -> datetime:
    return Arrow.fromdatetime(dt, tzinfo='Asia/Shanghai').shift(**kwargs).datetime


def is_holiday(dt: datetime):
    """ 判断是否法定节假日 """
    dt = shift_dt(dt, days=0)
    year, month = dt.year, dt.month
    for s, e in LAW_HOLIDAYS[year]:
        s, e = shift_dt(s, days=0), shift_dt(e, days=0)
        if s.month > month:
            break
        if e.month < month:
            continue
        if s <= dt <= e:
            return True
    weekday = dt.weekday()
    if weekday in [5, 6] and dt.strftime(DEFAULT_DATE_FORMAT) not in ADJUST_WORKDAYS[year]:
        return True
    return False


def is_weekend(dt: datetime | str):
    """ 判断是否周末 """
    if isinstance(dt, str):
        dt = datetime.strptime(dt, DEFAULT_DATE_FORMAT)
    return not is_holiday(dt) and not is_workday(dt)


def is_workday(dt):
    """ 判断是否工作日 """
    if isinstance(dt, str):
        dt = arrow.get(dt)
    dt = shift_dt(dt, days=0)
    year, month = dt.year, dt.month
    for s, e in LAW_HOLIDAYS[year]:
        s, e = shift_dt(s, days=0), shift_dt(e, days=0)
        if s.month > month:
            break
        if e.month < month:
            continue
        if s <= dt <= e:
            return False
    weekday = dt.weekday()
    if weekday in [5, 6] and dt.strftime(DEFAULT_DATE_FORMAT) not in ADJUST_WORKDAYS[year]:
        return False
    return True


def get_holidays(start: datetime, end: datetime):
    """
    获取所有法定节假日
    :param start:
    :param end:
    :return:
    """
    holidays = []
    date, end = shift_dt(start, days=0), shift_dt(end, days=0)
    while date <= end:
        if is_holiday(date):
            holidays.append(date)
        date = shift_dt(date, days=1)
    return holidays


def get_workdays(start, end):
    """
    获取所有工作日
    :param start:
    :param end:
    :return:
    """
    start, end = shift_dt(start, days=0), shift_dt(end, days=0)
    assert start <= end, 'start can not be large than end'
    workdays = []
    while start <= end:
        if is_workday(start):
            workdays.append(start)
        start = shift_dt(start, days=1)
    return workdays


def get_monthly_workdays(year=None, month=None):
    """
    根据月份获取所有工作日
    :param year:
    :param month:
    :return:
    """
    years = LAW_HOLIDAYS.keys()
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    if year:
        years = [year]
    if month:
        months = [month]
    data = {}
    for y in years:
        for m in months:
            start = datetime(year=y, month=m, day=1)
            end = shift_dt(datetime(year=y + 1, month=1, day=1), days=-1)
            workdays = get_workdays(start, end)
            data[f'{y}-{m}'] = dict(
                year=y,
                month=m,
                workdays=workdays
            )
    return data
