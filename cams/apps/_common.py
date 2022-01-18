"""CAMs 데이터를 다운로드 하는 페이지"""

print(f"<{__name__}> loading...")

from db import sensor
from db.group import Group
from db.user import AppUser
from db.sensor import Sensor
from db.location import Location
from ._imports import *
import pandas as pd

from dash.dash_table import DataTable
import dash.dash_table.Format as dtFmt

from pymongo import MongoClient
from bson.raw_bson import RawBSONDocument
import psycopg2 as pg
import psycopg2.extensions as pge
import psycopg2.extras as pga

from db.sensor_data import sd_cols, sd_cols_meta, sd_cols_raw, sd_cols_meta_raw
from db import sensor_data as sd
from db._mongo import ReadMongo
from utility import loadAppSettings

# pd.DataFrame column type
_types = {x: "float64" for x in sd_cols}
_types.update({x: "string" for x in sd_cols_meta})
_types_mongo = {x: "float64" for x in sd_cols_raw}
_types_mongo.update({x: "string" for x in sd_cols_meta_raw})

# dash.DataTable header
sd_headers = [
    "T-air",
    "T-leaf",
    "RH[%]",
    "Light",
    "CO₂",
    "DP",
    "EvaTrans",
    "HD",
    "VPD",
]
_headers_meta = [
    # "ID",
    "Group",
    "Location",
    "Sensor",
    "Time",
]

# dash.DataTable columns
_dt_columns = [
    {
        "name": h,
        "id": c,
        "type": "numeric",
        "format": dtFmt.Format(
            precision=3, scheme=dtFmt.Scheme.decimal_si_prefix
        ),  # fixed)
    }
    # 시간 + 측정값 컬럼 전체
    for h, c in zip([_headers_meta[3], *sd_headers], [sd_cols_meta[3], *sd_cols])
]


def _query_data(
    group_id, sensor_id, location_id, startDati, endDati, dp
) -> pd.DataFrame:
    """DB에서 주어진 기간동안의 데이터를 불러온다
    - group_id, sensor_id, location_id가 0일 경우 무시
    - dp가 0일 경우 DB데이터 그대로 출력
    """

    ds, cols = sd.Select(group_id, sensor_id, location_id, startDati, endDati, dp)
    df = pd.DataFrame(ds)
    debug(_query_data, f"{startDati}~{endDati}: {df.shape = }")
    if len(ds) > 0:
        if dp:
            cols[cols.index(f"time{dp}")] = "time"
        df.columns = cols

    if df.shape[0] and df.shape[1]:
        df = df.astype(_types, copy=False)  # , errors="ignore")
        df.set_index("time")  # , inplace=True)

    return df


def _query_data_mongo(sn: str, startDati) -> pd.DataFrame:
    """MongoDB에서 하루동안의 데이터를 불러온다."""

    dics = ReadMongo(sn, startDati, asCursor=True)
    df = pd.DataFrame(dics)   

    if df.shape[0] and df.shape[1]:
        df = df.astype(_types_mongo, copy=False)  # , errors="ignore")
        cols = [str(c).lower() for c in df.columns]
        df.columns = cols
        df.set_index("time")  # , inplace=True)
    debug(_query_data_mongo, f"{startDati}: {df.shape = }")    

    return df


def parse_and_load(
    sensor_id, location_id, start_date_str, end_date_str, dp
) -> pd.DataFrame:
    """UI 데이터를 파싱하고 디비에 쿼리하여 DataFrame 리턴"""

    startDati = datetime.strptime(start_date_str, "%Y-%m-%d")
    endDati = datetime.strptime(end_date_str, "%Y-%m-%d")
    dbmsKey = getSettings("Cams")["DbmsKey"]
    if dbmsKey == "Postgres":
        user: AppUser = fli.current_user
        group_id = 0 if user.level >= 2 else user.group.id  # master's group_id -> 0
        df = _query_data(group_id, sensor_id, location_id, startDati, endDati, dp)
    elif dbmsKey == "Mongo":
        sn = Sensor.query.get(sensor_id).sn
        df = _query_data_mongo(sn, startDati)
    return df


def build_data_table(df: pd.DataFrame) -> DataTable:
    """pandas.DataFrame을 dash.DataTable로 변환한다."""

    data = df.to_dict("records") if df is not None else []

    table = DataTable(
        id="apps-export-dt-table",
        columns=_dt_columns,
        data=data,
        style_cell=dict(textAlign="right", paddingRight="5px"),
        style_header=dict(textAlign="center"),
        cell_selectable=False,
        page_size=15,
        row_selectable="multi",
    )
    return table


# test
def test():
    # df1 = parse_and_load(1, 1, "2021-12-15", "2021-12-15", 5)
    df1 = parse_and_load(1, 1, "2022-01-18", "2022-01-18", 5)
    dt1 = build_data_table(df1)
    json = dt1.to_plotly_json()
    print(json)

# test()
