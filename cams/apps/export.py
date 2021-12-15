"""CAMs 데이터를 다운로드 하는 페이지"""

print(f"<{__name__}> loading...")

from ._imports import *
import pandas as pd

from dash.dash_table import DataTable
from dash.dash_table.Format import Format, Scheme, Trim

# from db.user import AppUser
# from db.farm import Farm
# from db.sensor import Sensor
from utility import parseDate

from pymongo import MongoClient
from bson.raw_bson import RawBSONDocument
import psycopg2 as pg
import psycopg2.extensions as pge
import psycopg2.extras as pga

_set = getSettings("Postgres")
_pgc = pg.connect(
    f'postgres://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)

# _farms = []  # fli.current_useruser.farms
# sensors = {}

# build data types of columns
_cols = [
    "air_temp",
    "leaf_temp",
    "humidity",
    "light",
    "co2",
    "dewpoint",
    "evapotrans",
    "hd",
    "vpd",
]
_types = {x: "float64" for x in _cols}
_meta_cols = ["id", "time", "sensor_id", "location_id", "group_id"]
_types.update({x: "string" for x in _meta_cols})
_headers = [
    # "Sensor",
    # "Location",
    # "Organization",
    "Tair",
    "Tleaf",
    "RH[%]",
    "Time",
    "Light",
    "CO₂",
    "DP",
    "EvaTrans",
    "HD",
    "VPD",
]

_dt_columns = [
    {
        "name": h,
        "id": c,
        "type": "numeric",
        "format": Format(precision=3, scheme=Scheme.decimal_si_prefix),  # fixed)
    }
    for h, c in zip(_headers, _meta_cols + _cols)
]


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")

    # 센서 ID 추출
    locs = fli.current_user.group.locations
    sensors = fli.current_user.group.sensors
    # for f in locs:
    #     _sensors.update({s.id: s for s in f.sensors})

    dateValue = datetime.now().date()
    snOptions = [{"label": sensors[s].name, "value": s} for s in sensors]
    snDefalut = snOptions[0]["value"] if len(snOptions) > 0 else ""

    headerRow = html.H4(
        [
            html.Span("cloud_download", className="material-icons-two-tone"),
            html.Span("Export CAMs Data", className="font-sc"),
        ],
        className="flex-h",
    )
    sensorRow = html.Label(
        [
            html.Span("CAMs Sensor"),
            html.Span("sensors", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="apps-export-sensor",
                options=snOptions,
                value=snDefalut,
                clearable=False,
                searchable=False,
            ),
        ],
        className="apps-export-label",
    )
    dateRow = html.Label(
        [
            html.Span("Date Range"),
            html.Span("date_range", className="material-icons-two-tone"),
            dcc.DatePickerRange(
                id="apps-export-date",
                display_format="YYYY-MM-DD",
                start_date=dateValue,
                end_date=dateValue,
                updatemode="bothdates",
                minimum_nights=0,
            ),
        ],
        className="apps-export-label",
    )

    buttonRow = html.Div(
        [
            html.Span(
                id="apps-export-rows"
            ),  # [html.Span(id="apps-export-rows"), " rows"]),
            html.Span("_", className="material-icons-two-tone"),
            html.Button(
                [
                    html.Span("download", className="material-icons-outlined"),
                    html.Span("Export as CSV", className="font-sc"),
                ],
                id="apps-export-button",
                n_clicks=0,
            ),
            dcc.Download(id="apps-export-download"),
        ],
        className="apps-export-label",
    )

    return html.Div(
        [
            html.Header(headerRow, id="app-export-header"),
            html.Section(sensorRow),
            html.Section(dateRow),
            html.Section(buttonRow, id="apps-export-button-section"),
            html.Section("-- data table --", id="apps-export-dt-section"),
        ],
        id="app-export-container",
    )


def load_data(sn, start, end) -> pd.DataFrame:
    """DB에서 주어진 기간동안의 데이터를 불러온다"""

    try:
        # cursor: pge.cursor = _pgc.cursor()
        cursor: pge.cursor = _pgc.cursor(cursor_factory=pga.DictCursor)

        # sql = cursor.mogrify(
        #     """SELECT * FROM sensor_data
        #     WHERE (sensor_id = (SELECT id FROM sensor WHERE sn = %s))
        #     AND (date(time) = %s)
        #     ORDER BY time DESC LIMIT 10000""",
        #     (sn, start),
        # )
        sql = cursor.mogrify(
            """SELECT * FROM sensor_data 
            WHERE (sensor_id = (SELECT id FROM sensor WHERE sn = %s)) 
            AND (time BETWEEN %s AND %s)
            ORDER BY time DESC LIMIT 10000""",
            (sn, start, end),
        )

        cursor.execute(sql)
        cols = [x.name for x in cursor.description]
        ds = cursor.fetchall()
        # global _df
        df = pd.DataFrame(ds)
        debug(load_data, f"{start}~{end}: {df.shape = }")
        if len(ds) > 0:
            df.columns = cols
    finally:
        cursor.close()

    if df.shape[0] and df.shape[1]:
        # types = {x: ("float64" if x in _cols else "string") for x in cols}
        # df = df.astype(types, copy=False)  # , errors="ignore")
        df = df.astype(_types, copy=False)  # , errors="ignore")
        # df["time_key"] = [parseDate(d, t) for d, t in zip(df["Date"], df["Time"])]
        # df.set_index("time_key", inplace=True)
        df.set_index("time")

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


@app.callback(
    Output("apps-export-dt-section", "children"),
    Output("apps-export-rows", "children"),
    Input("apps-export-sensor", "value"),
    Input("apps-export-date", "start_date"),
    Input("apps-export-date", "end_date"),
)
def update_ui(sensor_id, start_date, end_date):

    if not sensor_id or not start_date or not end_date:
        return no_update

    sensors = fli.current_user.group.sensors
    sn = sensors[sensor_id].sn
    start = date.fromisoformat(start_date).strftime("%Y%m%d")
    end = date.fromisoformat(end_date).strftime("%Y%m%d")

    df = load_data(sn, start, end)
    dt = build_data_table(df)

    return dt, f"{df.shape[0]}"


@app.callback(
    Output("apps-export-download", "data"),
    Input("apps-export-button", "n_clicks"),
    State("apps-export-sensor", "value"),
    State("apps-export-date", "start_date"),
    State("apps-export-date", "end_date"),
    prevent_initial_call=True,
)
def exportAsCsv(n, sensor_id, start_date, end_date):
    """export data as csv"""

    if not sensor_id or not start_date or not end_date:
        return no_update

    sensors = fli.current_user.group.sensors
    sn = sensors[sensor_id].sn
    start = date.fromisoformat(start_date).strftime("%Y%m%d")
    end = date.fromisoformat(end_date).strftime("%Y%m%d")

    df = load_data(sn, start, end)

    if not df.shape[0] or not df.shape[1]:
        return no_update

    sensorName = sensors[sensor_id].name.replace(" ", "-")
    fn = f"{sensorName}_{start_date}~{end_date}.csv"
    cols = _meta_cols + _cols
    return dcc.send_data_frame(
        df.to_csv,
        fn,
        # sep="\t",
        float_format="%.2f",
        columns=cols,
        index=False,
    )


# 이 페이지를 메인 메뉴바에 등록한다.
addPage(layout, "DataExport", 40)


# test
import json


def test():
    df1 = load_data("B2F_CAMs_2000000000001", "20211215", "20211215")
    dt1 = build_data_table(df1)
    # txt = json.dumps(dt1)
    # debug(txt)


test()
