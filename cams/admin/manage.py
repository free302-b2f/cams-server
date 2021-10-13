"""메타데이터 관리 화면"""

from admin._common import *
from admin._imports import *
from admin._add_farm import *
from admin._add_sensor import *


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")

    global g_users, g_farms, g_sensors

    userOptions = [{"label": u.username, "value": u.id} for u in g_users]
    userDefalut = userOptions[0]["value"] if len(userOptions) > 0 else ""

    headerRow = html.H4(
        [
            html.Span("settings", className="material-icons-two-tone"),
            html.Span("Manage Farm & Sensor", className="font-sc"),
        ],
        className="flex-h",
    )

    userRow = html.Label(
        [
            html.Span("User"),
            html.Span("badge", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="admin-manage-user",
                options=userOptions,
                value=userDefalut,
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
                id="admin-manage-farm-add",
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
                "delete_forever",
                className="material-icons-outlined",
                id="admin-manage-sensor-add",
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

    user = AppUser.query.get(uid)
    farms = user.farms
    farmOptions = [{"label": f.name, "value": f.id} for f in farms]
    farmDefalut = farmOptions[0]["value"] if len(farmOptions) > 0 else ""

    return farmOptions, farmDefalut


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-farm", "value"),
)
def onFarm(fid):
    """Farm 선택시 sensor목록 업데이트"""

    if not fid:
        return no_update

    farm = Farm.query.get(fid)
    sensors = farm.sensors
    sensorOptions = [{"label": s.name, "value": s.id} for s in sensors]
    sensorDefalut = sensorOptions[0]["value"] if len(sensorOptions) > 0 else ""

    return sensorOptions, sensorDefalut



add_page(layout, "Add-Farm")
