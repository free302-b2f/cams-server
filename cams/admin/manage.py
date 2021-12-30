"""메타데이터 관리 화면"""

print(f"<{__name__}> loading...")

from ._common import *

# from ._imports import *
from ._location import *
from ._sensor import *
from ._user import *


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

    locationRow = html.Label(
        [
            html.Span("Location"),
            html.Span("yard", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="admin-manage-location",
                clearable=False,
                searchable=False,
            ),
            html.Span(
                "clear",
                className="material-icons-outlined",
                id="admin-manage-location-clear",
                n_clicks=0,
            ),
            html.Span(
                "delete",
                className="material-icons-outlined",
                id="admin-manage-location-delete",
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
            html.Section(locationRow),
            html.Section(sensorRow),
            userSection,
            locationSection,
            sensorSection,
        ],
        id="admin-manage-container",
    )


# AppUser 선택시 location/sensor 목록 업데이트
@app.callback(
    Output("admin-manage-user-username", "value"),
    Output("admin-manage-user-email", "value"),
    Output("admin-manage-user-realname", "value"),
    Output("admin-manage-user-level", "value"),
    Output("admin-manage-user-level-label", "hidden"),
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-user", "value"),
)
def onUser(uid):
    """AppUser 선택시 location/sensor 목록 업데이트"""

    if not uid:
        return no_update

    # user: AppUser = fli.current_user
    user: AppUser = AppUser.query.get(uid)

    return [
        user.username,
        user.email,
        user.realname,
        user.level,
        False if user.level >= 2 else True,
        *buildSensorOptions(uid),
        *buildLocationOptions(uid),
    ]


@app.callback(
    Output("admin-manage-location-name", "value"),
    Output("admin-manage-location-desc", "value"),
    Input("admin-manage-location", "value"),
)
def onFarm(fid):
    """Farm 선택시 업데이트"""

    if not fid:
        return "", ""

    loc = Location.query.get(fid)

    # return *buildSensorOptions(fid), farm.name
    return loc.name, loc.desc


@app.callback(
    Output("admin-manage-sensor-name", "value"),
    Output("admin-manage-sensor-sn", "value"),
    Input("admin-manage-sensor", "value"),
)
def onSensor(sid):
    """Sensor 선택시 업데이트"""

    if not sid:
        return "", ""

    sensor = Sensor.query.get(sid)

    return sensor.name, sensor.sn


addPage(layout, "Admin")
