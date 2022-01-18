"""MongoDB 연결을 위한 공통 기능"""

from typing import Dict
import pymongo
import utility as util
from pymongo import MongoClient
from bson.raw_bson import RawBSONDocument
from bson.objectid import ObjectId
from datetime import date, datetime, time, timedelta, timezone


def _connectMongo():
    set = util.loadAppSettings("Mongo")
    mc = MongoClient(
        f'mongodb://{set["User"]}:{set["Pw"]}@{set["Ip"]}:{set["Port"]}/{set["Db"]}',
        # document_class=RawBSONDocument,
    )
    dsMG = mc[set["Db"]]["sensors"]

    return mc, dsMG


def InsertMongo(dic: Dict):
    try:
        mc, ds = _connectMongo()
        dic.pop("_id")
        x = ds.insert_one(dic)  # DB inserting
    finally:
        mc.close()


def ReadMongo(sn: str, date, time=None, asCursor:bool = False):  # return dict
    """MongoDB에서 date 일 time 시각 sn의 레코드를 읽어들임"""

    try:
        mc, ds = _connectMongo()
        # .strftime("%Y%m%d") .strftime("%H:%M:%S")
        keys = {"SN": sn, "Date": date.strftime("%Y%m%d")}
        if time:
            keys["Time"] = time.strftime("%H:%M:%S")
        docs = ds.find(keys).sort("Time", pymongo.ASCENDING)
        return docs if asCursor else list(docs)
    finally:
        mc.close()


def ReadMongoBetween(start: str):  # return dict
    """MongoDB에서 start 시각부터 end 날의 모든 레코드를 읽어들임"""

    try:
        mc, ds = _connectMongo()
        # .strftime("%Y%m%d") .strftime("%H:%M:%S")

        dics = []
        keys = {"_id": {"$gt": ObjectId(start)}}
        docs = ds.find(keys).sort("_id", pymongo.ASCENDING)
        dics = list(docs)
        lastId = str(dics[-1]["_id"]) if len(dics) > 0 else start
        return dics, lastId
    finally:
        mc.close()


def _ReadMongoBetween(start: str, end: str = None):  # return dict
    """MongoDB에서 start 시각부터 end 날의 모든 레코드를 읽어들임"""

    try:
        mc, ds = _connectMongo()
        # .strftime("%Y%m%d") .strftime("%H:%M:%S")

        # ----> 처음/끝 문서 로딩시간이 많이 걸림 --> 현재 값의로 하드코딩
        # firstDoc = ds.find().sort([("_id", 1), ("Date", 1), ("Time", 1)]).limit(1)[0]
        # lastDoc = ds.find().sort([("_id", -1), ("Date", -1), ("Time", -1)]).limit(1)[0]
        # firstDati = util.parseDate(firstDoc["Date"], firstDoc["Time"])
        # lastDati = util.parseDate(lastDoc["Date"], lastDoc["Time"])
        firstDati = datetime(2020, 1, 1)
        # lastDati = datetime.now() #datetime(2021, 11, 8, 15, 18)

        startDati = start if start > firstDati else firstDati
        startDate = startDati.date()
        startTime = startDati.time()
        startTimeFilter = {"$gte": startTime.strftime("%H:%M:%S")}

        endDati = end if end != None else datetime.now()
        endDate = endDati.date()
        endTime = endDati.time()
        endTimeFilter = {"$lte": endTime.strftime("%H:%M:%S")}

        dics = []
        oneDay = timedelta(days=1)
        curDate = startDate
        while curDate <= endDate:
            # {"Date": Date, "Time": {"$gte": "00:00:30", "$lte": "23:59:30"}}
            keys = {"Date": curDate.strftime("%Y%m%d")}
            timeFilter = {}
            if curDate == startDate:
                timeFilter.update(startTimeFilter)
            if curDate == endDate:
                timeFilter.update(endTimeFilter)
            keys["Time"] = timeFilter
            docs = ds.find(keys).sort("_id", pymongo.ASCENDING)
            # docs = ds.find(keys).sort("Time", pymongo.ASCENDING)
            dics.extend(list(docs))
            curDate = curDate + oneDay

        lastDoc = dics[-1]
        # lastDati = util.parseDate(lastDoc["Date"], lastDoc["Time"])
        lastDati = f'{lastDoc["_id"]}'
        return dics, lastDati
    finally:
        mc.close()
