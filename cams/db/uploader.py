"""CAMs 장비의 업로드를 흉내낸다"""

print(f"<{__name__}> loading...")

if __name__ == "__main__" or not __package__:
    # 단독실행시 db 패키지 초기화 생략 (flask context 없이)
    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    from _mongo import ReadMongo
    import sensor_data as sd
else:
    from ._mongo import ReadMongo
    from . import sensor_data as sd

from time import sleep
from datetime import date, datetime, time, timedelta, timezone


def run():
    """MongoDB에서 읽어서 SN과 시간을 수정하여 Postgresql에 추가"""

    while True:
        # 레코드 생성: MongoDB에서 읽어오기
        now = datetime.now()
        sec = 30 if now.second > 15 and now.second < 45 else 0
        ti = time(hour=now.hour, minute=now.minute, second=sec)
        dati = datetime(2021, 3, now.day, **ti)
        dics = ReadMongo("B2F_CAMs_1000000000002", dati, dati)

        # 레코드 수정: 테스트 센서, 오늘 날짜로 변경
        sn = "B2F_CAMs_2000000000002"
        dati = datetime(now.year, now.month, now.day, **ti)
        dbDate = dati.strftime("%Y%m%d")
        dbTime = dati.strftime("%H:%M:%S")

        # Postgresql에 추가
        for dic in dics:
            dic["SN"] = sn
            dic["Date"] = dbDate
            dic["Time"] = dbTime
            print(f"inserting: {sn} {dati}")

            sd.InsertRawDic(dic)

        sleep(30)


if __name__ == "__main__":
    # dics = ReadMongo("B2F_CAMs_1000000000002", datetime(2021, 3, 1))
    run()
# else:
#     import threading
#     _thread = threading.Thread(target=run, args=())
#     _thread.daemon = True
#     _thread.start()
