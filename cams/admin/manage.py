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
        html.H5(
            [
                html.Span("settings", className="material-icons-two-tone"),
                html.Span("Manage Group Users/Locations/Sensors", className="font-sc"),
            ],
            className="flex-h",
        )
    )

    confirm = dcc.ConfirmDialog(
        id="admin-manage-confirm",
        # message="그룹삭제...\n그룹 소속 모든 데이터가 삭제됩니다!\n삭제할까요?",
        displayed=False,
    )
    confirm.trigger = ""  # 확인창을 호출한 소스

    return html.Div(
        [
            headerSection,
            buildGroupSection(),
            buildUserSection(),
            buildLocationSection(),
            buildSensorSection(),
            confirm,
        ],
        id="admin-manage-container",
    )


@app.callback(
    Input("admin-manage-confirm", "trigger"),
    Input("admin-manage-confirm", "message"),
    Output("admin-manage-confirm", "displayed"),
    prevent_initial_call=True,
)
def onDeleteClick(src, msg):
    """확인 대화상자"""

    return True if src and msg else no_update


@app.callback(
    Output("admin-manage-group-name", "value"),
    Output("admin-manage-group-desc", "value"),
    Output("admin-manage-user", "options"),
    Output("admin-manage-user", "value"),
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Output("admin-manage-sensor-location", "options"),
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-group", "value"),
    prevent_initial_call=True,
)
def onGroup(gid):
    """Group 선택시 user/location/sensor 목록 업데이트"""

    if gid == None or gid == "":
        return no_update

    group = Group.query.get(gid)
    if group == None:
        return no_update

    locOpt = buildLocationOptions(gid)

    return [
        group.name,
        group.desc,
        *buildUserOptions(gid),
        *locOpt,
        locOpt[0],
        *buildSensorOptions(gid),
    ]


@app.callback(
    Output("admin-manage-user-group", "options"),
    Output("admin-manage-user-group", "value"),
    Output("admin-manage-user-username", "value"),
    Output("admin-manage-user-email", "value"),
    Output("admin-manage-user-realname", "value"),
    Output("admin-manage-user-level-label", "hidden"),
    Output("admin-manage-user-level", "options"),
    Output("admin-manage-user-level", "value"),
    Input("admin-manage-user", "value"),
    prevent_initial_call=True,
)
def onUser(uid):
    """AppUser 선택시  업데이트"""

    if not uid:
        return no_update

    user: AppUser = AppUser.query.get(uid)
    groupOptions, _ = buildGroupOptions()
    showLevel = True if len(groupOptions) else False
    options = buildLevelOptions()[0] if showLevel else no_update

    return [
        groupOptions,
        user.group_id,
        user.username,
        user.email,
        user.realname,
        not showLevel,
        options,
        user.level,
    ]


@app.callback(
    Output("admin-manage-location-name", "value"),
    Output("admin-manage-location-desc", "value"),
    Input("admin-manage-location", "value"),
    prevent_initial_call=True,
)
def onLocation(fid):
    """Location 선택시 업데이트"""

    if not fid:
        return "", ""

    loc = Location.query.get(fid)
    return loc.name, loc.desc


@app.callback(
    # Output("admin-manage-sensor-group", "value"),
    Output("admin-manage-sensor-name", "value"),
    Output("admin-manage-sensor-sn", "value"),
    Output("admin-manage-sensor-location", "value"),
    Output("admin-manage-sensor-active", "value"),
    Input("admin-manage-sensor", "value"),
    prevent_initial_call=True,
)
def onSensor(id):
    """Sensor 선택시 업데이트"""

    # admin-manage-sensor-location은 그룹 변경시 한번만 갱신하면 되지만
    # 그럴경우

    if not id:
        return no_update

    sensor: Sensor = Sensor.query.get(id)

    # return sensor.group_id, sensor.name, sensor.sn, sensor.location_id
    return sensor.name, sensor.sn, sensor.location_id, [True] if sensor.active else []


addPage(layout, "Admin")
