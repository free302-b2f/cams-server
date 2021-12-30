"""MongoDB 연결을 위한 공통 기능"""

import pymongo
import utility as util
from pymongo import MongoClient
from bson.raw_bson import RawBSONDocument
from datetime import date, datetime, time, timedelta, timezone


def _connectMongo():
    set = util.loadAppSettings("Mongo")
    mc = MongoClient(
        f'mongodb://{set["User"]}:{set["Pw"]}@{set["Ip"]}:{set["Port"]}/{set["Db"]}',
        # document_class=RawBSONDocument,
    )
    dsMG = mc[set["Db"]]["sensors"]

    return mc, dsMG


def ReadMongo(sn: str, date, time=None):  # return dict
    """MongoDB에서 date 일 time 시각 sn의 레코드를 읽어들임"""

    try:
        mc, ds = _connectMongo()
        # .strftime("%Y%m%d") .strftime("%H:%M:%S")
        keys = {"SN": sn, "Date": date.strftime("%Y%m%d")}
        if time:
            keys["Time"] = time.strftime("%H:%M:%S")
        docs = ds.find(keys).sort("_id", pymongo.ASCENDING)
        return list(docs)
    finally:
        mc.close()
