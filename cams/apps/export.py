"""CAMs 데이터를 다운로드 하는 페이지"""

print(f"<{__name__}> loading...")

from ._common import *


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")

    # 헤더 
    headerRow = html.H5(
        [
            html.Span("cloud_download", className="material-icons-two-tone"),
            html.Span("Export CAMs Data", className="font-sc"),
            dcc.Loading(
                type="circle",
                fullscreen=True,
                id="apps-export-loading1",
            ),
            dcc.Loading(
                type="circle",
                fullscreen=True,
                id="apps-export-loading2",
            ),
        ],
        className="flex-h",
    )

    # 위치 목록
    user: AppUser = fli.current_user
    locs = {
        l.id: l
        for l in (Location.query.all() if user.is_master() else user.group.locations)
    }
    locOptions = [{"label": "ALL", "value": 0}]
    locOptions.extend(
        [
            {"label": f"{l}: {locs[l].group.name} - {locs[l].name}", "value": l}
            for l in locs
        ]
    )
    locDefault = locOptions[1]["value"] if len(locOptions) > 1 else 0
    locationRow = html.Label(
        [
            html.Span("Location"),
            html.Span("yard", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="apps-export-location",
                options=locOptions,
                value=locDefault,
                clearable=False,
                searchable=False,
            ),
        ],
        className="apps-export-label",
    )

    # 센서 목록
    sensors = {
        s.id: s
        for s in (Sensor.query.all() if user.is_master() else user.group.sensors)
    }
    sensorOptions = [{"label": "ALL", "value": 0}]
    sensorOptions.extend(
        [
            {"label": f"{s}: {sensors[s].group.name} - {sensors[s].name}", "value": s}
            for s in sensors
        ]
    )
    locSensors = locs[locDefault].sensors if len(locs) else []
    sensorDefault = locSensors[0].id if len(locSensors) else 0  # 위치의 첫 센서
    sensorRow = html.Label(
        [
            html.Span("CAMs Sensor"),
            html.Span("sensors", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="apps-export-sensor",
                options=sensorOptions,
                value=sensorDefault,
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

    # 데이터 포인트 목록
    dpOptions = [
        {"label": "평균 데이터 (5분 간격)", "value": 5},
        {"label": "전체 데이터 (30초 간격)", "value": 0},
    ]

    dpRow = html.Label(
        [
            html.Span("Data Point"),
            html.Span("_", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="apps-export-dp",
                options=dpOptions,
                value=5,
                clearable=False,
                searchable=False,
            ),
        ],
        className="apps-export-label",
    )

    # 실행 버튼
    buttonRow = html.Div(
        [
            html.Span(id="apps-export-rows"),
            html.Span("_", className="material-icons-two-tone"),
            html.Button(
                [
                    html.Span("download", className="material-icons-outlined"),
                    html.Span("Export as CSV", className="font-sc"),
                ],
                id="apps-export-button",
                n_clicks=0,
            ),
            dcc.Download(id="apps-export-download", base64=True),
        ],
        className="apps-export-label",
    )

    return html.Div(
        [
            html.Header(headerRow, id="app-export-header"),
            html.Section(locationRow),
            html.Section(sensorRow),
            html.Section(dateRow),
            html.Section(dpRow),
            html.Section(buttonRow, id="apps-export-button-section"),
            html.Section("-- data table --", id="apps-export-dt-section"),
        ],
        id="app-export-container",
    )


@app.callback(
    Output("apps-export-dt-section", "children"),
    Output("apps-export-rows", "children"),
    Output("apps-export-loading1", "children"),
    Input("apps-export-location", "value"),
    Input("apps-export-sensor", "value"),
    Input("apps-export-date", "start_date"),
    Input("apps-export-date", "end_date"),
    Input("apps-export-dp", "value"),
)
def update_ui(location_id, sensor_id, start_date, end_date, dp):
    """UI 변경에 따른 업데이트 수행"""

    df = parse_and_load(location_id, sensor_id, start_date, end_date, dp)
    if df is None:
        return no_update
    dt = build_data_table(df)

    return dt, f"{df.shape[0]}", no_update


@app.callback(
    Output("apps-export-download", "data"),
    Output("apps-export-loading2", "children"),
    Input("apps-export-button", "n_clicks"),
    State("apps-export-location", "value"),
    State("apps-export-sensor", "value"),
    State("apps-export-date", "start_date"),
    State("apps-export-date", "end_date"),
    State("apps-export-dp", "value"),
    prevent_initial_call=True,
)
def exportAsCsv(n, location_id, sensor_id, start_date, end_date, dp):
    """export data as csv"""

    df = parse_and_load(location_id, sensor_id, start_date, end_date, dp)
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

    # columns to export
    # cols = sd_cols_meta + sd_cols
    # BOM 없으면 Excel에서 한글 깨짐 - 엑셀이 UTF-8 인식 못함
    csv = df.to_csv(
        # sep="\t",
        float_format="%.2f",
        columns=df.columns,
        index=False,
        # encoding="utf-8-sig", # pandas==1.4.1: BOM 적용 안됨-버그?
        # mode="w",
    )
    data = dcc.send_string(csv, fn)

    # insert BOM
    bytes = csv.encode(encoding="utf-8-sig")
    data = dcc.send_bytes(bytes, fn)

    return data, no_update


# 이 페이지를 메인 메뉴바에 등록한다.
addPage(layout, "Export", 40)
