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

from db.sensor_data import sd_cols, sd_cols_meta_join, sd_cols_raw, sd_cols_meta_raw
from db import sensor_data as sd
from db._mongo import ReadMongo
from utility import loadAppSettings

# 수정된 메타 컬럼명
_cols_meta = [x.replace("1", "") for x in sd_cols_meta_join]

# pd.DataFrame column type
_types = {x: "float64" for x in sd_cols}
_types.update({x: "string" for x in _cols_meta[0:3]})
# _types.update({_cols_meta[3]: "datetime64" })# 불필요

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

# dash.DataTable 에 보여줄 컬럼
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
    for h, c in zip([_headers_meta[3], *sd_headers], [_cols_meta[3], *sd_cols])
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
        # rename column
        for x, y in zip(sd_cols_meta_join, _cols_meta):
            cols[cols.index(x)] = y
        df.columns = cols

    if df.shape[0] and df.shape[1]:
        df = df.astype(_types, copy=False)  # , errors="ignore")
        # df.set_index(_cols_meta[3])  # , inplace=True)

    return df


def parse_and_load(
    location_id, sensor_id, start_date_str, end_date_str, dp
) -> pd.DataFrame:
    """UI 데이터를 파싱하고 디비에 쿼리하여 DataFrame 리턴"""

    startDati = datetime.strptime(start_date_str, "%Y-%m-%d")
    endDati = datetime.strptime(end_date_str, "%Y-%m-%d")
    user: AppUser = fli.current_user
    group_id = user.group.id
    df = _query_data(group_id, sensor_id, location_id, startDati, endDati, dp)

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
