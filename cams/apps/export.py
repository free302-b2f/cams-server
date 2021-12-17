"""CAMs 데이터를 다운로드 하는 페이지"""

print(f"<{__name__}> loading...")

from db.group import Group
from db.user import AppUser
from db.sensor import Sensor
from db.location import Location
from ._imports import *
import pandas as pd

from dash.dash_table import DataTable
import dash.dash_table.Format as dtFmt

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

# numeric columns
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

# meta columns ~ string type?
_meta_cols = ["id", "time", "sensor_id", "location_id", "group_id"]
_types.update({x: "string" for x in _meta_cols})

# dash.DataTable columns & headers
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
        "format": dtFmt.Format(precision=3, scheme=dtFmt.Scheme.decimal_si_prefix),  # fixed)
    }
    for h, c in zip(_headers, _meta_cols + _cols)
]


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")

    # 헤더
    headerRow = html.H4(
        [
            html.Span("cloud_download", className="material-icons-two-tone"),
            html.Span("Export CAMs Data", className="font-sc"),
        ],
        className="flex-h",
    )

    # 센서 선택 목록
    sensors = {s.id: s for s in fli.current_user.group.sensors}
    sensorOptions = [{"label": "ALL", "value": 0}]
    sensorOptions.extend([{"label": sensors[s].name, "value": s} for s in sensors])
    # snDefalut = snOptions[0]["value"] if len(snOptions) > 0 else ""
    sensorRow = html.Label(
        [
            html.Span("CAMs Sensor"),
            html.Span("sensors", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="apps-export-sensor",
                options=sensorOptions,
                value=0,
                clearable=False,
                searchable=False,
            ),
        ],
        className="apps-export-label",
    )

    # 위치 선택 목록
    locationOptions = [{"label": "ALL", "value": 0}]
    locationOptions.extend(
        [{"label": l.name, "value": l.id} for l in fli.current_user.group.locations]
    )
    locationRow = html.Label(
        [
            html.Span("Location"),
            html.Span("yard", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="apps-export-location",
                options=locationOptions,
                value=0,
                clearable=False,
                searchable=False,
            ),
        ],
        className="apps-export-label",
    )

    # 기간 선택 목록
    dateValue = datetime.now().date()
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
            html.Section(locationRow),
            html.Section(dateRow),
            html.Section(buttonRow, id="apps-export-button-section"),
            html.Section("-- data table --", id="apps-export-dt-section"),
        ],
        id="app-export-container",
    )


def _query_data(group_id, sensor_id, location_id, start, end) -> pd.DataFrame:
    """DB에서 주어진 기간동안의 데이터를 불러온다"""

    try:
        cursor: pge.cursor = _pgc.cursor()
        # cursor: pge.cursor = _pgc.cursor(cursor_factory=pga.DictCursor)

        format = "SELECT * FROM sensor_data WHERE (date(time) BETWEEN %s AND %s)"
        value = (start, end)
        if group_id > 0:
            format = f"{format} AND (group_id = %s)"
            value = (*value, group_id)
        if sensor_id > 0:
            format = f"{format} AND (sensor_id = %s)"
            value = (*value, sensor_id)
        if location_id > 0:
            format = f"{format} AND (location_id = %s)"
            value = (*value, location_id)
        format = f"{format} ORDER BY location_id ASc, sensor_id ASC, time ASC"
        sql = cursor.mogrify(format, value)
        debug(str(sql))

        cursor.execute(sql)
        cols = [x.name for x in cursor.description]
        ds = cursor.fetchall()
        df = pd.DataFrame(ds)
        debug(_query_data, f"{start}~{end}: {df.shape = }")
        if len(ds) > 0:
            df.columns = cols
    finally:
        cursor.close()

    if df.shape[0] and df.shape[1]:
        df = df.astype(_types, copy=False)  # , errors="ignore")
        # df["time_key"] = [parseDate(d, t) for d, t in zip(df["Date"], df["Time"])]
        # df.set_index("time_key", inplace=True)
        df.set_index("time")

    return df


def _build_data_table(df: pd.DataFrame) -> DataTable:
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


def parse_and_load(sensor_id, location_id, start_date, end_date) -> pd.DataFrame:
    """UI 데이터를 파싱하고 디비에 쿼리하여 DataFrame 리턴"""

    if sensor_id == None or location_id == None or not start_date or not end_date:
        return None

    user: AppUser = fli.current_user
    group_id = 0 if user.level >= 2 else user.group.id  # master's group_id -> 0
    start = date.fromisoformat(start_date).strftime("%Y%m%d")
    end = date.fromisoformat(end_date).strftime("%Y%m%d")

    df = _query_data(group_id, sensor_id, location_id, start, end)
    return df


@app.callback(
    Output("apps-export-dt-section", "children"),
    Output("apps-export-rows", "children"),
    Input("apps-export-sensor", "value"),
    Input("apps-export-location", "value"),
    Input("apps-export-date", "start_date"),
    Input("apps-export-date", "end_date"),
)
def update_ui(sensor_id, location_id, start_date, end_date):
    """UI 변경에 따른 업데이트 수행"""

    df = parse_and_load(sensor_id, location_id, start_date, end_date)
    if df is None:
        return no_update
    dt = _build_data_table(df)

    return dt, f"{df.shape[0]}"


@app.callback(
    Output("apps-export-download", "data"),
    Input("apps-export-button", "n_clicks"),
    State("apps-export-sensor", "value"),
    State("apps-export-location", "value"),
    State("apps-export-date", "start_date"),
    State("apps-export-date", "end_date"),
    prevent_initial_call=True,
)
def exportAsCsv(n, sensor_id, location_id, start_date, end_date):
    """export data as csv"""

    df = parse_and_load(sensor_id, location_id, start_date, end_date)
    if df is None:
        return no_update
    if not df.shape[0] or not df.shape[1]:
        return no_update

    g: Group = fli.current_user.group
    sensor: Sensor = Sensor.query.get(sensor_id)
    location: Location = Location.query.get(location_id)

    fn = g.name.replace(" ", "-")
    if sensor_id != 0:
        fn = f'{fn}__{sensor.name.replace(" ", "-")}'
    if location_id != 0:
        fn = f'{fn}__{location.name.replace(" ", "-")}'    
    fn = f"{fn}__{start_date}~{end_date}.csv"

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
    df1 = _query_data(1, 1, 1, "20211215", "20211215")
    dt1 = _build_data_table(df1)
    # txt = json.dumps(dt1)
    # debug(txt)


# test()
