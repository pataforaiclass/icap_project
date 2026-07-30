from datetime import datetime
from zoneinfo import ZoneInfo

# 查詢當前日期 & 時間(台灣時間)
def get_tw_time():
  now = datetime.now(ZoneInfo("Asia/Taipei"))

  ampm = "上午" if now.hour < 12 else "下午"

  hour = now.hour % 12
  if hour == 0:
    hour = 12

  return (
    f"{now.year}/{now.month}/{now.day} "
    f"{ampm}{hour}:{now.minute:02d}:{now.second:02d}"
  )