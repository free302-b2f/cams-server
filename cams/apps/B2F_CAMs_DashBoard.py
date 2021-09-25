"""
CAMs 센서데이터의 시각화
"""

if __name__ == "__main__":
    import sys, os.path as path

    dir = path.join(path.dirname(__file__), "..")
    sys.path.append(dir)

from dash_html_components.Label import Label
from dash_html_components.Td import Td
from apps.imports import *

debug("loading...")

_set = getConfigSection("Postgres")
_pgc = pg.connect(
    f'postgres://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)


def load_data(sn: str, date) -> Tuple[pd.DataFrame, List[str]]:
    """DB에서 하루동안의 데이터를 불러온다.
    DataFrame 변환시간의 리스트를 생성
    테이블의 필드이름 목록을 생성
    :return: DataFrame, 필드이름 목록의 튜플"""

    def query_postgres() -> Tuple[List, List[str]]:

        cursor: pge.cursor = _pgc.cursor()  # cursor_factory=pga.DictCursor)
        start = date
        sql = cursor.mogrify(
            """SELECT time, air_temp, leaf_temp, humidity, light, co2, dewpoint, evapotrans, hd, vpd 
            FROM sensor_data 
            WHERE (sensor_id = (SELECT id FROM sensor WHERE sn = %s)) 
            AND (date(time) = %s)
            ORDER BY time DESC LIMIT 10000""",
            (sn, start),
        )
        debug(f"{sql}")

        cursor.execute(sql)
        cols = [x.name for x in cursor.description]
        ds = cursor.fetchall()
        cursor.close()

        if not len(ds):
            cols.clear()

        return ds, cols

    ds, cols = query_postgres()
    df = pd.DataFrame(ds)  # .astype(data_types)
    df.columns = cols
    # df.pop('id')
    # cols.remove('id')
    debug(load_data, f"{date}: {df.shape = }, {cols= }")

    return (df, cols)


# load_data("B2F_CAMs_1000000000001", "20210216")  # test


def plot(df: pd.DataFrame, cols: List[str] = [], title: str = "B2F CAMs") -> dict:
    """데이터의 Figure 생성"""

    if df is None or len(df) == 0:
        return px.scatter(
            pd.DataFrame({x: [0] for x in cols}),
            y=cols,
            title=f"{title}",
        )

    df.sort_values(by=["time"], axis=0, inplace=True)
    cols.remove("time")

    return {
        "data": [go.Scatter(x=df["time"], y=df[i], mode="lines", name=i) for i in cols],
        "layout": go.Layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Data",
            # legend ={'itemwidth':30}
        ),
    }


# plot(query_sensors("", "B2F_CAMs_1000000000001", "20210117"), 'test plot') #test


@app.callback(
    Output("graph1", "figure"),
    Input("SN", "value"),
    Input("Date", "date"),
    # Input("sampling-ratio", "value"),
)
def update_graph(sensor_sn, date):  # , sampleRatio):
    """선택된 정보로 그래프를 업데이트 한다"""

    debug(update_graph, f"{sensor_sn = }, {date = }")
    # debug(update_graph, f"{SN = }, {date = }, {sampleRatio = }")

    # date == None
    if date is None:
        return plot(None)

    dbSN = sensor_sn  # TODO: use sensor_id
    dbDate = datetime.fromisoformat(date).strftime("%Y%m%d")
    df, cols = load_data(dbSN, dbDate)

    # resampling pdands.Frame
    # frac = (float(sampleRatio) if (sampleRatio is not None) else 100) / 100.0
    # if frac < 1:
    #     df = df.sample(frac=frac)
    fig = plot(df, cols, f"{dbSN} : {dbDate}")

    return fig


# @app.callback(Output("cams-sr-label", "children"), Input("sampling-ratio", "value"))
# def update_time(sampleRatio):
#     """샘플링 비율에 따른 샘플간격을 업데이트 한다"""

#     frac = (float(sampleRatio) if (sampleRatio != None) else 0) / 100.0
#     minuites =0.5 / frac
#     return f"{0.5 / frac} minutes"


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")
    app.title = "B2F - CAMs Viewer"

    # 센서 ID 추출
    user = fli.current_user
    farms = user.farms
    sensors = []
    for f in farms:
        sensors.extend(f.sensors)
    ids = {x.sn: x.id for x in sensors}

    def tr(label: str, el, elId: str = None, merge: bool = False):
        """주어진 내용을 html TR에 출력한다"""

        if merge:
            tr = html.Tr(
                html.Td(
                    el,
                    style={"width": "100%", "padding": "2px 5px"},
                    colSpan="10",
                    className="cams_table_td",
                )
            )
        else:
            tr = html.Tr(
                [
                    html.Td(
                        html.Label(label, htmlFor=elId if (elId != None) else label),
                        style={"width": "20%", "padding": "2px 5px"},
                        className="cams_table_td",
                    ),
                    html.Td(
                        el,
                        style={"width": "50%", "padding": "2px 5px"},
                        className="cams_table_td",
                    ),
                    html.Td(
                        "",
                        style={"width": "100%", "padding": "2px 5px"},
                        className="cams_table_td",
                    ),
                ]
            )
        return tr

    dateValue = datetime.now().date()
    snOptions = [{"label": sn, "value": sn} for sn in ids]
    snDefalut = snOptions[0]["value"] if len(snOptions) > 0 else ""

    sensorTr = html.Tr(
        html.Td(
            html.Label(
                [
                    html.Span("Sensor"),
                    dcc.Dropdown(id="SN", options=snOptions, value=snDefalut),
                ]
            ),
            colSpan="10",
        ),
    )
    dateTr = html.Tr(
        html.Td(
            html.Label(
                [
                    html.Span("Date"),
                    dcc.DatePickerSingle(
                        id="Date",
                        display_format="YYYY-MM-DD",
                        date=dateValue,
                    ),
                ],
            ),
            colSpan="10",
        )
    )
    fracTr = tr(
        "Sample Ratio(%)",
        [
            dcc.Input(
                id="sampling-ratio",
                value="100",
                type="number",
                min=0,
                max=100,
                step=1,
                debounce=True,
            ),
            html.Span("100%", id="cams-sr-label"),
        ],
        "sampling-ratio",
    )
    graphTr = [
        html.Tr(
            [
                html.Td(
                    dcc.Graph(id="graph1", className="camsGraphBorder"),
                ),
                html.Td(
                    dcc.Graph(id="graph2", className="camsGraphBorder"),
                ),
                html.Td(),
            ],
            className="apps-cams-table-tr",
        ),
        html.Tr(
            [
                html.Td(
                    dcc.Graph(id="graph3", className="camsGraphBorder"),
                ),
                html.Td(
                    dcc.Graph(id="graph4", className="camsGraphBorder"),
                ),
                html.Td(),
            ],
            className="apps-cams-table-tr",
        ),
    ]

    return html.Div(
        [
            html.H3("Bit2Farm CAMs Viewer"),
            # html.Hr(),
            html.Table(
                [
                    # tr("", "", merge=True),
                    sensorTr,
                    dateTr,
                    # fracTr,
                    *graphTr,
                ],
                className="cams_contents_table",
            ),  # ~table
        ],
        id="app-cams-container",
    )


# 이 페이지를 메인 메뉴바에 등록한다.
add_page(layout, "CAMs Viewer", 40)


if __name__ == "__main__":
    layout()
    # load_data("B2F_CAMs_1000000000001", "20200216")  # test
