import datetime

# 获取当前时间
now_time = datetime.datetime.now()
print(type(now_time))
# 当前时间减去一天 获得昨天当前时间
yes_time = now_time + datetime.timedelta(hours=+7)
# 格式化输出
yes_time_str = yes_time.strftime('%Y-%m-%d %H:%M:%S')
print(yes_time_str)

