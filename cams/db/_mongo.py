"""MongoDB 연결을 위한 공통 기능"""

from sensor_data import sd_cols, sd_cols_meta
import utility as util
from pymongo import MongoClient
from bson.raw_bson import RawBSONDocument
from datetime import date, datetime, time, timedelta, timezone

sd_cols_mongo = [
    "Air_Temp",
    "Leaf_Temp",
    "Humidity",
    "Light",
    "CO2",
    "Dewpoint",
    "EvapoTranspiration",
    "HD",
    "VPD",
]
PG_2_MG = {p: m for p, m in zip(sd_cols, sd_cols_mongo)}


def _connectMongo():
    set = util.loadAppSettings("Mongo")
    mc = MongoClient(
        f'mongodb://{set["User"]}:{set["Pw"]}@{set["Ip"]}:{set["Port"]}/{set["Db"]}',
        document_class=RawBSONDocument,
    )
    dsMG = mc[set["Db"]]["sensors"]

    return mc, dsMG


def _convert(r):

    dic = dict()
    dic["time"] = util.parseDate(r["Date"], r["Time"])
    dic["sn"] = r["SN"]

    for p in PG_2_MG:  
        dic[p] = r[PG_2_MG[p]]

    return dic


def ReadMongo(dt, sn:str): # return dict
    """dsMG에서 date일의 sn의 레코드를 읽어들임"""

    mc, ds = _connectMongo()
    dbDate = dt.strftime("%Y%m%d") # .strftime("%Y%m%d") .strftime("%H:%M:%S")
    dbTime = dt.strftime("%H:%M:%S")
    docs = ds.find({"Date": dbDate, "Time": dbTime, "SN": sn})
    dics = [_convert(r) for r in docs]

    mc.close()
    
    return dics