"""메타데이터 관리 화면"""

from admin._common import *
from admin._imports import *
from admin._add_farm import *
from admin._add_sensor import *


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")

    headerRow = html.H4(
        [
            html.Span("settings", className="material-icons-two-tone"),
            html.Span("Manage Farm & Sensor", className="font-sc"),
        ],
        className="flex-h",
    )

    userOpt = buildUserOptions()
    userRow = html.Label(
        [
            html.Span("User"),
            html.Span("badge", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="admin-manage-user",
                options=userOpt[0],
                value=userOpt[1],
                clearable=False,
                searchable=False,
            ),
        ],
        className="admin-manage-label",
    )

    farmRow = html.Label(
        [
            html.Span("Farm"),
            html.Span("yard", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="admin-manage-farm",
                clearable=False,
                searchable=False,
            ),
            html.Span(
                "clear",
                className="material-icons-outlined",
                id="admin-manage-farm-clear",
                n_clicks=0,
            ),
            html.Span(
                "delete",
                className="material-icons-outlined",
                id="admin-manage-farm-delete",
                n_clicks=0,
            ),
        ],
        className="admin-manage-label",
    )

    sensorRow = html.Label(
        [
            html.Span("CAMs"),
            html.Span("sensors", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="admin-manage-sensor",
                clearable=False,
                searchable=False,
            ),
            html.Span(
                "clear",
                className="material-icons-outlined",
                id="admin-manage-sensor-clear",
                n_clicks=0,
            ),
            html.Span(
                "delete",
                className="material-icons-outlined",
                id="admin-manage-sensor-delete",
                n_clicks=0,
            ),
        ],
        className="admin-manage-label",
    )

    return html.Div(
        [
            html.Header(headerRow),
            html.Section(userRow),
            html.Section(farmRow),
            html.Section(sensorRow),
            addFarmSection,
            addSensorSection,
        ],
        id="admin-manage-container",
    )


@app.callback(
    Output("admin-manage-farm", "options"),
    Output("admin-manage-farm", "value"),
    Input("admin-manage-user", "value"),
)
def onUser(uid):
    """AppUser 선택시 farm/sensor 목록 업데이트"""

    if not uid:
        return no_update

    return buildFarmOptions(uid)


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Output("admin-manage-farm-name", "value"),
    Input("admin-manage-farm", "value"),
)
def onFarm(fid):
    """Farm 선택시 sensor목록 업데이트"""

    if not fid:
        return no_update, no_update, ""
    
    farm = Farm.query.get(fid)

    return *buildSensorOptions(fid), farm.name



@app.callback(
    Output("admin-manage-sensor-name", "value"),
    Output("admin-manage-sensor-sn", "value"),
    Output("admin-manage-sensor-desc", "value"),
    Input("admin-manage-sensor", "value"),
)
def onSensor(sid):
    """Sensor 선택시 업데이트"""

    if not sid:
        return "", "", ""

    sensor = Sensor.query.get(sid)

    return sensor.name, sensor.sn, sensor.desc


add_page(layout, "Add-Farm")
