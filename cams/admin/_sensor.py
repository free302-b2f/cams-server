"""센서 추가 화면"""

from ._common import *
from dash.dependencies import Input, Output, State
from db import sensor_data as sd


def buildSensorSection():
    """Sensor의 빈 목록 및 편집 섹션을 생성"""

    # calc permissions
    user: AppUser = fli.current_user
    isPrivate = getSettings("Cams", "IS_PRIVATE_SERVER")
    isMaster, isGAdmin, isNormal, _ = user.is_levels()
    canAdd = isMaster or isGAdmin
    canUpdate = isMaster or isGAdmin or isNormal
    canDelete = isMaster or isGAdmin
    canUpdateSn = isMaster or isGAdmin
    canUpdateActive = isMaster or isGAdmin
    showGroup = isMaster  # == canUpdateGroup

    list = buildLabel_Dropdown(
        "센서 관리",
        "sensor",
        None,
        [],
        None,
        "sensors",
        [("clear", "delete")] if canDelete else None,
    )
    group = buildLabel_Dropdown(
        "Group", "sensor", "group", *buildGroupOptions(), hidden=not showGroup
    )

    name = buildLabel_Input(
        "Sensor Name", "sensor", "name", "", Sensor.max_name, not canUpdate
    )
    sn = buildLabel_Input(
        "Sensor SN", "sensor", "sn", "", Sensor.max_sn, not canUpdateSn
    )
    locs = buildLabel_Dropdown(
        "Location", "sensor", "location", [], None, "", hidden=not canUpdate
    )
    active = buildLabel_Check(
        "Active(Receive Data)", "sensor", "active", not canUpdateActive
    )

    button = buildButtonRow("sensor", canAdd, not canUpdate)

    return html.Section(
        [
            # html.Hr(),
            list,
            group,
            name,
            sn,
            locs,
            active,
            button,
        ],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-sensor-add", "n_clicks"),
    State("admin-manage-group", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    State("admin-manage-sensor-location", "value"),
    prevent_initial_call=True,
)
def onAddClick(n, gid, name, sn, locId):
    """<Add> 버튼 작업 및 sensor 목록 업데이트"""

    if not n:
        return no_update

    try:
        model = Sensor(name=name, sn=sn, group_id=gid, location_id=locId)

        db = fl.g.dba.session
        db.add(model)
        db.commit()
        return buildSensorOptions(gid, model.id)
    except:
        return no_update


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Output("admin-manage-confirm", "submit_n_clicks"),
    Input("admin-manage-sensor-save", "n_clicks"),
    State("admin-manage-sensor-group", "value"),
    State("admin-manage-sensor", "value"),
    State("admin-manage-confirm", "submit_n_clicks"),
    prevent_initial_call=True,
)
def onUpdateClick(n, gid, id, nSubmit):
    """<Update> 확인"""

    if not n or not id or gid == None or gid == "":
        return no_update

    model: Sensor = Sensor.query.get(id)
    if model == None:
        return no_update

    if model.group_id != gid:
        # 소유 그룹이 바뀌는 경우 -> 확인 후 진행
        group: Group = Group.query.get()
        msg = f"센서 {model}의 소유자를 {group}으로 바꾸겠습니까까?"
        return "sensor-update", msg, no_update
    else:
        # 소유 그룹이 바뀌지 않는 경우 -> 확인없이 업데이트 진행
        return no_update, no_update, 1 + 0 if not nSubmit else nSubmit


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-sensor", "value"),
    State("admin-manage-sensor-group", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    State("admin-manage-sensor-location", "value"),
    prevent_initial_call=True,
)
def onUpdateConfirmed(n, id, gid, name, sn, locId):
    """<Update> 작업 및 목록 업데이트"""

    if not n:
        return no_update

    try:
        model: Sensor = Sensor.query.get(id)
        model.name = name
        model.sn = sn

        gidSrc = model.group_id
        changingGroup = gid != gidSrc
        if changingGroup:  # 센서 이전 작업: 새 그룹의 보관소로 이동
            group: Group = Group.query.get(gid)
            sensor = Sensor.query.filter_by(group_id=gid, sn=sn).first()
            if sensor is None:  # 새 센서 만들고 보관소로 이동
                sensor = Sensor(group_id=gid, sn=sn, name=name)
            else:
                pass

            model.location_id = group.storage_id
            # model.group_id = gidDest
        else:
            model.location_id = locId

        dba = fl.g.dba
        dba.session.commit()
        return buildSensorOptions(gidSrc, id if not changingGroup else None)
    except:
        return no_update


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Input("admin-manage-sensor-delete", "n_clicks"),
    State("admin-manage-sensor", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, id):
    """<Delete> 버튼 확인 대화상자"""

    if not n or not id:
        return no_update

    model: Sensor = Sensor.query.get(id)
    if model == None:
        return no_update

    numRows = sd.Count(sensor_id=id)
    # numRows = db.execute(sql).fetchone()[0]
    # numRows = next(iter(numRows.fetchone() or []), None)
    msg = f"센서를 삭제하면 센서의 측정데이터 <{numRows}>개도 모두 삭제됩니다."
    msg = f"{msg}\n\n센서 {model}를 삭제할까요?"
    return "sensor", msg


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-confirm", "trigger"),
    State("admin-manage-sensor", "value"),
    prevent_initial_call=True,
)
def onDeleteConfirmed(n, src, id):
    """<Delete> 버튼 작업 - 센서 삭제, 센서데이터가 있으면 삭제 안함"""

    if not n or src != "sensor":
        return no_update

    try:
        model: Sensor = Sensor.query.get(id)
        if model == None:
            return no_update

        # 데이터 삭제
        user: AppUser = fli.current_user
        if user.is_master() or user.is_gadmin():
            sd.f1_clear_data(id)

        # 센서 삭제
        db = fl.g.dba.session
        db.delete(model)
        db.commit()
        return buildSensorOptions(model.group_id)
    except:
        return no_update
