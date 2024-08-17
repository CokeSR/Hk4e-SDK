import pytz
from datetime import datetime, timezone

# 时间转换
# 获取中国时区的时间对象
def get_chinaDT(timestamp):
    utc_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    china_tz = pytz.timezone("Asia/Shanghai")
    china_dt = utc_dt.astimezone(china_tz)
    return china_dt


# 将时间戳转换为 MySQL DATETIME 格式（中国时区）
def timestamp_to_datetime(timestamp):
    china_dt = get_chinaDT(timestamp)
    sql_datetime = china_dt.strftime("%Y-%m-%d %H:%M:%S")
    return sql_datetime


# 将中国时区的 datetime 对象转换为时间戳
def datetime_to_timestamp(china_dt):
    if isinstance(china_dt, str):
        # 如果 china_dt 是字符串，将其转换回 datetime 对象
        china_dt = datetime.strptime(china_dt, "%Y-%m-%d %H:%M:%S")
        china_tz = pytz.timezone("Asia/Shanghai")
        china_dt = china_tz.localize(china_dt)
    timestamp_back = china_dt.timestamp()
    return int(timestamp_back)
