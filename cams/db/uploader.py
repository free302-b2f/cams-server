"""CAMs 장비의 업로드를 흉내낸다"""

if __name__ == "__main__":
    import sys, os.path as path

    dir = path.join(path.dirname(__file__), "..")
    sys.path.append(dir)

from apps.imports import *
import threading
from time import sleep

# region ---- DB Server & Connection ----

_setMg = getConfigSection("Mongo")
_mongoClient = MongoClient(
    f'mongodb://{_setMg["User"]}:{_setMg["Pw"]}@{_setMg["Ip"]}:{_setMg["Port"]}/{_setMg["Db"]}',
    document_class=RawBSONDocument,
)
_sensors = _mongoClient[_setMg["Db"]]["sensors"]

# endregion


def _seed():
    """7개월전 데이터를 현재 날짜로 복사"""

    now = datetime.now()
    date = datetime(2021, 2, now.day).strftime("%Y%m%d")
    sec = 30 if now.second > 15 and now.second < 45 else 0
    time = datetime(2021, 2, 15, hour=now.hour, minute=now.minute, second= sec).strftime("%H:%M:%S")
    print(f"copying: {date} {time}")

    dsSrc = _sensors.find(
        {"Date": date, "Time": time}
    )
    for r in dsSrc:
        dic = {
            "FarmName": r["FarmName"],
            "SN": r["SN"],
            "Date": now.strftime("%Y%m%d"),
            "Time": r["Time"],
        }
        val = {
            "Leaf_Temp": r["Leaf_Temp"],
            "Light": r["Light"],
            "Air_Temp": r["Air_Temp"],
            "Humidity": r["Humidity"],
            "Dewpoint": r["Dewpoint"],
            "CO2": r["CO2"],
            "EvapoTranspiration": r["EvapoTranspiration"],
            "HD": r["HD"],
            "VPD": r["VPD"],
        }
        dic.update(val)
        x = _sensors.insert_one(dic)  # DB inserting


def _run():
    while True:
        _seed()
        sleep(30)


if __name__ == "__main__":
    _run()
else:
    _thread = threading.Thread(target=_run, args=())
    _thread.daemon = True
    _thread.start()