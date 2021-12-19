"""CAMs 데이터를 다운로드 하는 페이지"""

print(f"<{__name__}> loading...")

from ._common import *


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
    dt = build_data_table(df)

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

    cols = sd_cols_meta + sd_cols
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
