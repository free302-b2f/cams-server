"""CAMs 장비의 업로드를 흉내낸다"""

print(f"<{__name__}> loading...")

if __name__ == "__main__":
    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    print(f"{dir= }")
    sys.path.insert(0, dir)

from time import sleep
from datetime import date, datetime, time, timedelta, timezone
from _mongo import ReadMongo
import sensor_data as sd


def run():
    """MongoDB에서 읽어서 Postgresql에 추가"""

    while True:
        now = datetime.now()
        sec = 30 if now.second > 15 and now.second < 45 else 0
        timeDic = dict(hour=now.hour, minute=now.minute, second=sec)
        dt = datetime(2021, 3, now.day, **timeDic)

        dics = ReadMongo(dt, "B2F_CAMs_1000000000002")
        sn = "B2F_CAMs_2000000000002"
        dt = datetime(now.year, now.month, now.day, **timeDic)

        for r in dics:
            r["sn"] = sn
            r["time"] = dt
            print(f"inserting: {sn} {dt}")
            sd.Insert(r)

        sleep(30)


if __name__ == "__main__":
    run()
# else:
#     import threading
#     _thread = threading.Thread(target=run, args=())
#     _thread.daemon = True
#     _thread.start()
