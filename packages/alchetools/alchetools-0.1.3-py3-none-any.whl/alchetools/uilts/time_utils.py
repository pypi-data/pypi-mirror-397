# -*- coding: utf-8 -*-
# @Author : Liu宗鑫
# @Time : 2024/11/8 下午3:22
# @File : time_utils.py
# @Software: PyCharm
import time
from datetime import datetime, timedelta

# 定义常用时间格式
FORMAT_STR = "%Y-%m-%d %H:%M:%S"  # 默认时间格式
DATE_FORMAT = "%Y-%m-%d"  # 年月日格式
TIME_FORMAT = "%H:%M:%S"  # 时分秒格式
TIME_FORMAT_DIGIT = "%H%M%S"  # 时分秒数字格式
NUMBER_FORMAT = "%Y%m%d%H%M%S"  # 数字格式


def get_current_time(format_str=FORMAT_STR):
    """
    获取当前时间并格式化为指定格式。

    :param format_str: 时间格式字符串，默认值为 "%Y-%m-%d %H:%M:%S"
    :return: 格式化后的当前时间字符串
    """
    if not isinstance(format_str, str):
        raise TypeError("format_str 必须是字符串类型")

    try:
        # 获取当前时间
        current_time = datetime.now()
        # 格式化当前时间
        formatted_time = current_time.strftime(format_str)
        return formatted_time
    except ValueError as e:
        raise ValueError(f"格式化时间失败，请检查 format_str 是否有效: {e}")


def get_current_year():
    """
    获取当前年份。

    :return: 当前年份字符串，例如 "2024"
    """
    return datetime.now().strftime("%Y")


def get_current_month():
    """
    获取当前月份。

    :return: 当前月份字符串，例如 "11"
    """
    return datetime.now().strftime("%m")


def get_current_day():
    """
    获取当前日期中的日。

    :return: 当前日期中的日字符串，例如 "08"
    """
    return datetime.now().strftime("%d")


def get_13_timestamp():
    """
    获取当前时间的 13 位时间戳（毫秒级）。

    :return: 13 位时间戳（字符串类型）
    """
    timestamp = int(time.time() * 1000)
    return str(timestamp)


def convert_time(input_data, format_str=FORMAT_STR, to_timestamp=False):
    """
    在时间戳与时间字符串之间转换。

    :param input_data: 输入的数据，可以是 13 位时间戳（整数或字符串）或时间字符串
    :param format_str: 时间格式，默认值为 "%Y-%m-%d %H:%M:%S"
    :param to_timestamp: 控制转换方向
        - True: 将时间字符串转换为 13 位时间戳
        - False: 将 13 位时间戳转换为时间字符串
    :return: 转换后的数据（时间字符串或 13 位时间戳）
    """
    try:
        if to_timestamp:
            # 将时间字符串转换为 13 位时间戳
            dt_obj = datetime.strptime(input_data, format_str)
            return int(dt_obj.timestamp() * 1000)
        else:
            # 将 13 位时间戳转换为时间字符串
            seconds = int(input_data) / 1000
            dt_obj = datetime.fromtimestamp(seconds)
            return dt_obj.strftime(format_str)
    except (ValueError, TypeError) as e:
        raise ValueError(f"时间转换失败，请检查输入数据和格式是否有效: {e}")


def is_today_in_days(days):
    """
    判断今天是否在指定的星期列表中。

    :param days: list[str] 或 str，包含要匹配的星期名称，例如 ["周一", "周二"] 或 "周一"
    :return: bool，今天是否是指定的星期
    """
    import datetime

    # 将中文星期与数字对应
    day_map = {"周一": 0, "周二": 1, "周三": 2, "周四": 3, "周五": 4, "周六": 5, "周日": 6, }

    # 获取今天是星期几（0=周一，1=周二，...，6=周日）
    today_weekday = datetime.datetime.now().weekday()

    # 如果传入的是字符串，转为列表处理
    if isinstance(days, str):
        days = [days]

    # 转换输入的中文星期为数字
    target_days = {day_map[day] for day in days if day in day_map}

    # 判断今天是否在目标星期集合中
    return today_weekday in target_days


def get_week_day():
    """
    获取今天是星期几
    :return:
    """
    import datetime
    day_map = {"周一": 0, "周二": 1, "周三": 2, "周四": 3, "周五": 4, "周六": 5, "周日": 6}
    # 翻转字典
    day_map = dict(zip(day_map.values(), day_map.keys()))
    today_weekday = datetime.datetime.now().weekday()
    return day_map.get(today_weekday)


def shift_time(time_str, format_str=FORMAT_STR, days=0, hours=0, minutes=0, seconds=0):
    """
    对传入的时间字符串进行加减运算，并返回同格式的时间字符串。

    :param time_str: 原始时间字符串，例如 "2024-11-08 15:30:00"
    :param format_str: time_str 的格式，例如 "%Y-%m-%d %H:%M:%S"
    :param days: 要增加/减少的天数（可以为负数）
    :param hours: 要增加/减少的小时数（可以为负数）
    :param minutes: 要增加/减少的分钟数（可以为负数）
    :param seconds: 要增加/减少的秒数（可以为负数）
    :return: 偏移后的时间字符串（与 format_str 格式一致）
    """
    if not isinstance(time_str, str):
        raise TypeError("time_str 必须是字符串类型")

    if not isinstance(format_str, str):
        raise TypeError("format_str 必须是字符串类型")

    try:
        # 1. 把字符串解析为 datetime
        dt = datetime.strptime(time_str, format_str)

        # 2. 构造时间偏移（可以正可以负）
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        # 3. 计算新时间
        new_dt = dt + delta

        # 4. 按原格式输出
        return new_dt.strftime(format_str)
    except Exception as e:
        raise ValueError(f"时间偏移失败，请检查 time_str 和 format_str 是否匹配: {e}")