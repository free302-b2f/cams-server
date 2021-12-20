"""MongoDB 연결을 위한 공통 기능"""

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


def ReadMongo(dt, sn:str): # return dict
    """dsMG에서 date일의 sn의 레코드를 읽어들임"""

    try:
        mc, ds = _connectMongo()
        dbDate = dt.strftime("%Y%m%d") # .strftime("%Y%m%d") .strftime("%H:%M:%S")
        dbTime = dt.strftime("%H:%M:%S")
        docs = ds.find({"Date": dbDate, "Time": dbTime, "SN": sn})
        return list(docs)
    finally:
        mc.close()
    