from datetime import datetime, timedelta

mask = "%d.%m.%Y %H:%M"

s1 = "16.02.2023 15:00"
s2 = "17.02.2023 15:30"
s3 = "18.02.2023 16:00"

datetime_now = datetime.today()
delta = timedelta(days=0, hours=1, minutes=0, seconds=0)
date_from_dict = s2

ss = datetime_now + delta >= datetime.strptime(date_from_dict, mask) >= datetime_now - delta
print(ss)
