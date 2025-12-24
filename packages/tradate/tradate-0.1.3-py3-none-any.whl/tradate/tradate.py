import itertools
from datetime import datetime, timedelta

from .consts import TRADATE2025PATH, TRADATE2026PATH


def _load_dates() -> tuple[list[str], set[str], dict[str, str], dict[str, str]]:
    """加载交易日期数据并返回优化后的数据结构"""
    dates_list = [
        *(line.strip() for line in TRADATE2025PATH.read_text(encoding="utf-8").splitlines()),
        *(line.strip() for line in TRADATE2026PATH.read_text(encoding="utf-8").splitlines())

    ]
    dates_set = set(dates_list)

    date_prevdate = {
        next_date: current_date
        for current_date, next_date in itertools.pairwise(dates_list)
    }
    date_nextdate = {
        current_date: next_date
        for current_date, next_date in itertools.pairwise(dates_list)
    }

    return dates_list, dates_set, date_prevdate, date_nextdate


# 模块级别加载，避免重复加载
_DATES_LIST, _DATES_SET, _DATE_PREVDATE, _DATE_NEXTDATE = _load_dates()


def is_tradate(date: str) -> bool:
    """
    检查给定日期是否为交易日

    Args:
        date: 日期字符串，格式为'YYYY-MM-DD'，例如'2025-10-24'

    Returns:
        bool: 如果是交易日返回True，否则返回False
    """
    return date in _DATES_SET


def today_is_tradate() -> bool:
    """
    检查今天是否为交易日

    Returns:
        bool: 如果今天是交易日返回True，否则返回False
    """

    return is_tradate(datetime.now().strftime("%Y-%m-%d"))


def get_prev_date(date: str, fmt: str | None = None) -> str | None:
    """
    获取指定日期的前一个交易日

    Args:
        date: 日期字符串，格式为'YYYY-MM-DD'

    Returns:
        str: 前一个交易日，如果不存在则返回空字符串
    """
    ret = _DATE_PREVDATE.get(date, None)
    if fmt is None or ret is None:
        return ret
    return datetime.strptime(ret, "%Y-%m-%d").strftime(fmt)


def get_next_date(date: str, fmt: str | None = None) -> str | None:
    """
    获取指定日期的后一个交易日

    Args:
        date: 日期字符串，格式为'YYYY-MM-DD'

    Returns:
        str: 后一个交易日，如果不存在则返回空字符串
    """
    ret = _DATE_NEXTDATE.get(date, None)
    if fmt is None or ret is None:
        return ret
    return datetime.strptime(ret, "%Y-%m-%d").strftime(fmt)


def get_all_dates() -> list[str]:
    """
    获取所有交易日期列表（按顺序）

    Returns:
        List[str]: 按顺序排列的交易日期列表
    """
    return _DATES_LIST.copy()  # 返回副本以防止外部修改


def get_traday(fmt: str | None = None) -> str | None:
    """
    获取距今最近的交易日（包括今天，如果今天是交易日的话）

    Returns:
        str: 最近的交易日，格式为'YYYY-MM-DD'，如果没有找到返回空字符串
    """

    now = datetime.now()
    today: str = now.strftime("%Y-%m-%d")

    if is_tradate(today):
        return now.strftime(fmt) if fmt is not None else today

    # 否则向前查找最近的交易日
    delta = timedelta(days=1)
    # 最多向前查找365天，防止无限循环
    for _ in range(365):
        now -= delta
        if is_tradate(now.strftime("%Y-%m-%d")):
            return now.strftime(fmt if fmt is not None else "%Y-%m-%d")

    return None


def get_yestraday(fmt: str | None = None) -> str | None:
    """
    获取距今最近交易日的前一个交易日

    Returns:
        str: 最近交易日的前一个交易日，格式为'YYYY-MM-DD'，如果没有找到返回空字符串
    """
    troday = get_traday()
    if troday is None:
        return None

    return get_prev_date(troday, fmt)
