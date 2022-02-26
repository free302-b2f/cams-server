"""MongoDB 데이터를 Postgresql로 복사"""

print(f"<{__name__}> loading...")

if __name__ == "__main__" or not __package__:
    # 단독실행시 db 패키지 초기화 생략 (flask context 없이)
    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    from _mongo import ReadMongo, ReadMongoBetween, InsertMongo
    import sensor_data as sd
    from _postgresql import connect
else:
    from ._mongo import ReadMongo, ReadMongoBetween, InsertMongo
    from . import sensor_data as sd
    from ._postgresql import connect

from time import sleep
from datetime import date, datetime, time, timedelta, timezone
from utility import debug, loadAppSettings, info
from bson.objectid import ObjectId


# region ---- [cmd 0 : 하루치 데이터 복사] ----


def _copyDay(srcSN, destSN, srcDate, destDate=datetime.now()):
    """srcDate의 데이터를 destDays로 복사"""

    dics = ReadMongo(srcSN, srcDate)

    # Postgresql에 추가
    print(f"inserting: {destSN} : {srcDate} -> {destDate}")
    sd.InsertRawDics(dics, destSN, destDate)


def copy210215():
    """MongoDB 2021-02-15 데이터를 오늘 날짜로 복사"""

    srcDate = datetime(2021, 2, 15).date()

    # 복사할 장비 SN
    srcSN = "B2F_CAMs_1000000000001"
    destSN = "B2F_CAMs_2000000000001"
    _copyDay(srcSN, destSN, srcDate)

    # 복사할 장비 SN
    srcSN = "B2F_CAMs_1000000000002"
    destSN = "B2F_CAMs_2000000000002"
    _copyDay(srcSN, destSN, srcDate)


# endregion


# region ---- [cmd 1 : 실시간 장비업로드 흉내] ----


def _copyOne_M2P(srcSN, destSN):
    """MongoDB의 2021년 2월 현재 날짜의 현재 시각 데이터를 Postgresql에 복사"""

    now = datetime.now()
    sec = 0 if now.second < 30 else 30
    ti = dict(hour=now.hour, minute=now.minute, second=sec)
    dati = datetime(2021, 2, now.day % 28, **ti)
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
        print(f"inserting: {destSN} {dati} ({now})")

        sd.InsertRawDic(dic)
    pass


def _copyOne_M2M(srcSN, destSN):
    """2021년 2월 현재 날짜의 현재 시각 데이터를 복사"""

    now = datetime.now()
    sec = 0 if now.second < 30 else 30
    # now = now + timedelta(minutes=1)

    ti = dict(hour=now.hour, minute=now.minute, second=sec)
    dati = datetime(2021, 2, now.day % 28, **ti)
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
        print(f"inserting: {destSN} {dati} ({now})")

        InsertMongo(dic)
    pass


def simulate():
    """MongoDB에서 읽어서 SN과 시간을 수정하여 DB에 추가"""

    # 복사할 장비 SN
    srcSN = [
        "B2F_CAMs_1000000000001",
        "B2F_CAMs_1000000000002",
        "B2F_CAMs_1000000000001",
        "B2F_CAMs_1000000000002",
    ]
    destSN = [
        "B2F_CAMs_2000000000001",
        "B2F_CAMs_2000000000002",
        "B2F_CAMs_2000000000003",
        "B2F_CAMs_2000000000004",
    ]

    while True:
        t1 = datetime.now()

        for i in range(len(srcSN)):
            # _copyOne_M2P(srcSN[i], destSN[i])
            _copyOne_M2M(srcSN[i], destSN[i])

        sec = 30 - (datetime.now() - t1).total_seconds()
        if sec > 0:
            sleep(sec)


# endregion


# region ---- [cmd 2 : MongoDB -> Postgres 동기화 ] ----

_set = loadAppSettings("Cams")
_DB_START_DATI = datetime.fromisoformat(_set["DB_SYNC_START_DATE"])
_SYNCH_KEY = "db_uploader_last_synch"


def _get_last_synch() -> str:
    """마지막 싱크 작업 시각을 구한다"""

    try:
        pgc, cursor = connect()

        fmt = "SELECT text from Cams WHERE key = %s"
        sql = cursor.mogrify(fmt, (_SYNCH_KEY,))
        cursor.execute(sql)
        ds = cursor.fetchone()

        if ds == None:  # no record
            fmt = "INSERT INTO Cams (key, text) VALUES (%s,%s)"

            oid = ObjectId.from_datetime(_DB_START_DATI)  # (datetime(2022, 1, 17))
            txt = f"{oid}"
            values = (_SYNCH_KEY, txt)
            sql = cursor.mogrify(fmt, values)
            cursor.execute(sql)
            pgc.commit()
        else:
            txt = ds[0]

        # debug(f"{_SYNCH_KEY}= {txt}")
        return txt
    finally:
        cursor.close()
        pgc.close()


def _set_last_synch(lastId: str):
    """싱크 작업 시간을 저장한다"""

    try:
        pgc, cursor = connect()

        fmt = "UPDATE Cams SET text = %s WHERE key = %s"
        values = (lastId, _SYNCH_KEY)

        sql = cursor.mogrify(fmt, values)
        cursor.execute(sql)
        pgc.commit()
    finally:
        cursor.close()
        pgc.close()
    pass


def _save(dics):
    import json

    if len(dics) == 0:
        return

    with open("mongo.txt", "w") as fp:
        keys = sorted(dics[0].keys())
        keys.remove("_id")
        line = "\t".join(keys)
        fp.write(f"{line}\n")
        for dic in dics:
            line = "\t".join([dic[k] for k in keys])
            fp.write(f"{line}\n")
    pass


def sync_worker():
    """MonogDB에 새로 추가된 데이터를 Postgresql에 복사한다"""

    while True:
        t1 = datetime.now()

        try:
            start = _get_last_synch()
            dics, last = ReadMongoBetween(start)

            startDati = ObjectId(start).generation_time.astimezone()
            debug(f"{startDati} => {len(dics)}")
            # _save(dics)

            if len(dics) > 0:
                sd.InsertRawDics(dics)
                _set_last_synch(last)
        except:
            pass        

        sec = 30 - (datetime.now() - t1).total_seconds()
        if sec > 0:
            sleep(sec)


# endregion


if __name__ == "__main__":
    # 단독실행시 - 명령줄 분석 실행

    if len(sys.argv) < 2:
        pass
    elif sys.argv[1] == "0":
        copy210215()
    elif sys.argv[1] == "1":
        simulate()
    elif sys.argv[1] == "2":
        sync_worker()
    else:
        debug(f"invalid arugment: {sys.argv[1]}")
else:
    # 웹에서 실행시 - 동기화 쓰레드 시작
    import threading

    info(f"starting thread: sync_worker")
    _thread = threading.Thread(target=sync_worker, args=())
    _thread.daemon = True
    _thread.start()
