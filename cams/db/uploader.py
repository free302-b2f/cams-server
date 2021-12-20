"""CAMs 장비의 업로드를 흉내낸다"""

print(f"<{__name__}> loading...")

from time import sleep
from datetime import date, datetime, time, timedelta, timezone

# 단독실행시 db 패키지 초기화 생략 (flask context 없이)
if __name__ == "__main__" or not __package__:
    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    from _mongo import ReadMongo
    import sensor_data as sd
else:
    from ._mongo import ReadMongo
    from . import sensor_data as sd


def run():
    """MongoDB에서 읽어서 Postgresql에 추가"""

    while True:
        # 레코드 생성: MongoDB에서 읽어오기
        now = datetime.now()
        sec = 30 if now.second > 15 and now.second < 45 else 0
        timeDic = dict(hour=now.hour, minute=now.minute, second=sec)
        dt = datetime(2021, 3, now.day, **timeDic)
        dics = ReadMongo(dt, "B2F_CAMs_1000000000002")

        # 레코드 수정: 테스트 센서, 오늘 날짜로 변경
        sn = "B2F_CAMs_2000000000002"
        # .strftime("%Y%m%d") .strftime("%H:%M:%S")
        dt = datetime(now.year, now.month, now.day, **timeDic)

        # Postgresql에 추가
        for dic in dics:
            dic["SN"] = sn
            dic["Date"] = now.strftime("%Y%m%d")
            dic["Time"] = dt.strftime("%H:%M:%S")
            print(f"inserting: {sn} {dt}")

            sd.InsertRawDic(dic)

        sleep(30)


if __name__ == "__main__":
    run()
# else:
#     import threading
#     _thread = threading.Thread(target=run, args=())
#     _thread.daemon = True
#     _thread.start()
