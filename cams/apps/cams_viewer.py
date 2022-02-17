"""
CAMs 센서데이터의 시각화
"""

print(f"<{__name__}> loading...")

from ._common import *

# from ._imports import *
# import pandas as pd
from dash_extensions.enrich import Trigger
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

_col_header_map = {c: h for h, c in zip(sd_headers, sd_cols)}


def plotAll(df: pd.DataFrame, cols=[], title: str = "", colsRight=[]) -> dict:
    """데이터의 Figure 생성"""

    if df is None or not df.shape[0] or not df.shape[1]:
        return px.scatter(
            pd.DataFrame({x: [0] for x in cols}),
            y=cols,
            title=f"{title}",
        )

    df.sort_values(by=["time"], axis=0, inplace=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col in cols:
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df[col],
                mode="lines",
                name=col,
            ),
            secondary_y=False,
        )
    for col in colsRight:
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df[col],
                mode="lines",
                name=col,
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title=dict(text=title, yanchor="top", y=0.9, xanchor="center", x=0.5)
    )
    fig.update_layout(legend=dict(yanchor="bottom", y=1.05, xanchor="right", x=1.15))

    fig.update_xaxes(
        tickmode="auto",
        title="Time [hh:mm:ss]",
        # rangeslider_visible=True,
    )
    # fig.update_yaxes(tickmode="auto", tickformat=".3n", secondary_y=False)
    fig.update_yaxes(tickmode="auto", tickformat=".3n", secondary_y=True)

    # 범례 항목명 대체: evapotranspiration -> EvaTrans
    # fig.update_traces(name="EvaTrans", selector=dict(name="evapotranspiration"))
    def rename(old):
        new = _col_header_map[old]
        fig.update_traces(name=new, selector=dict(name=old))

    fig.for_each_trace(lambda sc: rename(sc.name))

    return fig


@app.callback(
    Output("apps-cams-graph1", "figure"),
    Output("apps-cams-graph2", "figure"),
    Output("apps-cams-graph3", "figure"),
    Output("apps-cams-graph4", "figure"),
    Input("apps-cams-sensor", "value"),
    Input("apps-cams-date", "date"),
    Trigger("apps-cams-interval", "n_intervals"),
)
def update_graph(sensor_id, date):
    """선택된 정보로 그래프를 업데이트 한다"""

    debug(update_graph, f"{sensor_id = }, {date = }")

    if date is None or not sensor_id:
        return plotAll(None), plotAll(None), plotAll(None), plotAll(None)

    sensor = Sensor.query.get(sensor_id)
    if sensor is None or sensor.group_id != fli.current_user.group.id:
        return plotAll(None), plotAll(None), plotAll(None), plotAll(None)

    df = parse_and_load(sensor_id, 0, date, date, 5)

    # "air_temp", "leaf_temp", "humidity", "light","co2", "dewpoint", "evapotranspiration","hd","vpd",

    # figure 1 : temperature vs light
    fig1 = plotAll(df, ["light"], "Light vs Temperature", ["air_temp", "leaf_temp"])
    fig1.update_yaxes(title_text="Light", secondary_y=False)
    fig1.update_yaxes(title_text="Temperature [ºC]", secondary_y=True)

    # figure 2 : temp~hum
    fig2 = plotAll(
        df, ["air_temp", "leaf_temp"], "Temperature vs Humidity", ["humidity"]
    )
    fig2.update_yaxes(title_text="Temperature(ºC)", secondary_y=False)
    fig2.update_yaxes(title_text="Humiidty(%)", secondary_y=True)

    # figure 3 : light~evatr
    fig3 = plotAll(df, ["light"], "Light vs EvapoTranspiration", ["evapotranspiration"])
    fig3.update_yaxes(title_text="Light", secondary_y=False)
    fig3.update_yaxes(title_text="EvapoTrans", secondary_y=True)
    # fig3.update_traces(name="EvaTrans", selector=dict(name="evapotranspiration"))

    # figure 4 : ALL
    fig4 = plotAll(df, sd_cols, "Time vs Various")
    fig4.update_yaxes(title_text="Quantities", secondary_y=False)
    fig4.update_xaxes(rangeslider_visible=True)
    fig4.update_layout(legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.95))

    return fig1, fig2, fig3, fig4


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")
    app.title = "B2F - CAMs Viewer"  # TODO: 효과없음

    # 센서 ID 추출
    sensors = {s.id: s for s in fli.current_user.group.sensors}
    sensorOptions = [{"label": sensors[s].name, "value": s} for s in sensors]
    snDefalut = sensorOptions[0]["value"] if len(sensorOptions) > 0 else ""
    sensorTr = html.Tr(
        [
            html.Td(
                html.Label(
                    [
                        html.Span("Sensor"),
                        dcc.Dropdown(
                            id="apps-cams-sensor",
                            options=sensorOptions,
                            value=snDefalut,
                            clearable=False,
                            searchable=False,
                        ),
                    ]
                ),
            ),
            html.Td(),
        ]
    )

    dateValue = datetime.now().date()
    dateTr = html.Tr(
        [
            html.Td(
                html.Label(
                    [
                        html.Span("Date"),
                        dcc.DatePickerSingle(
                            id="apps-cams-date",
                            display_format="YYYY-MM-DD",
                            date=dateValue,
                        ),
                    ],
                ),
            ),
            html.Td(),
        ],
    )

    def buildGraph(gId: int):
        return html.Div(
            [
                dcc.Graph(id=f"apps-cams-graph{gId}", className="apps-cams-graph"),
                html.Div(
                    "Tips:",
                    id=f"apps-cams-graph-info{gId}",
                    className="apps-cams-graph-info",
                ),
            ],
            id=f"apps-cams-graph-container{gId}",
            className=f"apps-cams-graph-container",
        )

    graphTr = [
        html.Tr(
            [
                html.Td(buildGraph(1)),
                html.Td(buildGraph(2)),
            ],
            className="apps-cams-table-tr",
        ),
        html.Tr(
            [
                html.Td(buildGraph(3)),
                html.Td(buildGraph(4)),
            ],
            className="apps-cams-table-tr",
        ),
    ]

    return html.Div(
        [
            html.H4(
                f"{fli.current_user.realname}'s CAMs",
                className="font-sc",
            ),
            # html.Hr(),
            html.Table(
                [
                    sensorTr,
                    dateTr,
                    *graphTr,
                ],
                className="app-cams-table",
            ),  # ~table
            dcc.Interval(
                id="apps-cams-interval",
                interval=30_000,  # in milliseconds
                n_intervals=0,
            ),
        ],
        id="app-cams-container",
    )


# 이 페이지를 메인 메뉴바에 등록한다.
addPage(layout, "CAMs Viewer", 20)


if __name__ == "__main__":
    layout()
    # load_data("B2F_CAMs_1000000000001", "20200216")  # test
    # plot(query_sensors("", "B2F_CAMs_1000000000001", "20210117"), 'test plot') #test
