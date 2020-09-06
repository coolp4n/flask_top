import time
from datetime import datetime, timedelta

"""
time : 产生时间戳
datetime.datetime： 时间转换模块
datetime.timedelta: 时间间隔模块
"""

# 时间戳 1970 ~ now 秒数
# 1599364325 10位
# 1599366058176 13位
timestamp = time.time()
print("时间戳[time.time()]:", timestamp)
print("======")
# 时间戳转换成日期
date = datetime.fromtimestamp(timestamp)
print("时间戳转换成日期[datetime.fromtimestamp]", date)
print(type(date))
print("======")

# 日期格式转换成日期字符串
# isoformat 标准时间格式
date_str = datetime.isoformat(date)
print("日期格式转换标准日期字符串[datetime.isoformat]:", date_str)
print(type(date_str))
print("======")

# 日期转换成自定义格式的日期字符串
date_str1 = datetime.strftime(date, "%Y-%m-%d  %H:%M:%s:%f")
print("自定义格式的日期字符串:", date_str1)
print(type(date_str1))

# 日期字符串转换成日期
# datetime.strptime()

print("======")
# 日期转换成时间戳
timestamp1 = datetime.timestamp(date)
print("日期转换成时间戳", timestamp1)
