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

# 복사할 장비 SN
srcSN = "B2F_CAMs_1000000000002"
destSN = "B2F_CAMs_2000000000002"


def _copyCurrentOne():
    """2021년 3월 현재 날짜의 현재 시각 데이터를 복사"""

    now = datetime.now()
    sec = 30 if now.second > 15 and now.second < 45 else 0
    ti = time(hour=now.hour, minute=now.minute, second=sec)
    dati = datetime(2021, 3, now.day, **ti)
    dics = ReadMongo(srcSN, dati, dati)

    # 레코드 수정: 테스트 센서, 오늘 날짜로 변경
    dati = datetime(now.year, now.month, now.day, **ti)
    dbDate = dati.strftime("%Y%m%d")
    dbTime = dati.strftime("%H:%M:%S")

    # Postgresql에 추가
    for dic in dics:
        dic["SN"] = destSN
        dic["Date"] = dbDate
        dic["Time"] = dbTime
        print(f"inserting: {destSN} {dati}")

        sd.InsertRawDic(dic)
    pass


def simulate():
    """MongoDB에서 읽어서 SN과 시간을 수정하여 Postgresql에 추가"""

    while True:
        _copyCurrentOne()
        sleep(30)


def _copyDay(srcDate, destDate=datetime.now()):
    """srcDate의 데이터를 destDays로 복사"""

    dics = ReadMongo(srcSN, srcDate)

    # Postgresql에 추가
    print(f"inserting: {destSN} : {srcDate} -> {destDate}")
    sd.InsertRawDics(dics, destSN, destDate)


def copy():
    """2021-02-15 데이터를 오늘 날짜로 복사"""

    src = datetime(2021, 2, 15).date()
    _copyDay(src)


if __name__ == "__main__":
    # simulate()
    copy()
# else:
#     import threading
#     _thread = threading.Thread(target=run, args=())
#     _thread.daemon = True
#     _thread.start()
