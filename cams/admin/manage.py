"""메타데이터 관리 화면"""

print(f"<{__name__}> loading...")

from ._common import *
from ._location import *
from ._sensor import *
from ._user import *
from ._group import *


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")

    headerSection = html.Header(
        html.H4(
            [
                html.Span("settings", className="material-icons-two-tone"),
                html.Span("Manage Locations & Sensors", className="font-sc"),
            ],
            className="flex-h",
        )
    )

    return html.Div(
        [
            headerSection,
            buildUserSection(),
            buildGroupSection(),
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
    Output("admin-manage-user-level", "options"),
    Output("admin-manage-user-level-label", "hidden"),
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
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

    user: AppUser = AppUser.query.get(uid)
    showLevel = fli.current_user.level >= 2
    options = buildLevelOptions()[0] if showLevel else no_update

    return [
        user.username,
        user.email,
        user.realname,
        user.level,
        options,
        not showLevel,
        *buildGroupOptions(uid),
        *buildSensorOptions(uid),
        *buildLocationOptions(uid),
    ]


@app.callback(
    Output("admin-manage-group-name", "value"),
    Output("admin-manage-group-desc", "value"),
    Input("admin-manage-group", "value"),
)
def onGroup(gid):
    """Location 선택시 업데이트"""

    if not gid:
        return "", ""

    grp = Group.query.get(gid)

    # return *buildSensorOptions(fid), farm.name
    return grp.name, grp.desc


@app.callback(
    Output("admin-manage-location-name", "value"),
    Output("admin-manage-location-desc", "value"),
    Input("admin-manage-location", "value"),
)
def onLocation(fid):
    """Location 선택시 업데이트"""

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
