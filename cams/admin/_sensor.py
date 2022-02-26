"""센서 추가 화면"""

from argparse import ArgumentError
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
    showGroup = False  # 소유그룹 변경 불가 -> 새그룹에서 생성해야 함

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
        "Active(Receive Data)", "sensor", "active", None, not canUpdateActive
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
            buildStatusRow("sensor"),
        ],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Output({"admin-manage-status-label": "sensor"}, "data"),
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
        model.activate()

        db = fl.g.dba.session
        db.add(model)
        db.commit()
        return *buildSensorOptions(gid, model.id), [f"{model} 추가완료", cnOk]
    
    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-sensor-active", "options"),
    Input("admin-manage-sensor-active", "value"),
    prevent_initial_call=True,
)
def onActiveChanged(active):
    """<Active> 체크박스 변경시 라벨을 선택에 맞게 변경"""

    if active is None:
        return no_update

    label = " 소유함 - 데이터 수신함" if True in active else " 소유하지 않음 - 데이터 수신하지 않음"
    options = [{"value": True, "label": label}]
    # debug(onActiveChanged, f"{active= }, {options= }")

    return options


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Output("admin-manage-confirm", "submit_n_clicks"),
    Output({"admin-manage-status-label": "sensor"}, "data"),
    Input("admin-manage-sensor-save", "n_clicks"),
    State("admin-manage-sensor", "value"),
    State("admin-manage-sensor-active", "value"),
    State("admin-manage-confirm", "submit_n_clicks"),
    prevent_initial_call=True,
)
def onUpdateClick(n, id, active, nSubmit):
    """<Update> 확인"""

    if not n or not id or active is None:
        return no_update

    try:
        model: Sensor = Sensor.query.get(id)
        if model == None:
            raise AdminError("삭제됨 - 존재하지 않는 레코드")

        if model.active != (len(active) > 0):  # 소유권이 바뀌는 경우 -> 확인 후 진행
            msg = f"센서 <{model.id}: {model.name}>를"
            if active:  # 소유권 가져오기
                msg = f"{msg} 활성화 -소유권 주장- 하겠습니까?"
                msg = f"{msg}\n SN= {model.sn}"
            else:
                msg = f"{msg} 비활성화 -소유권 포기- 하겠습니까?"
                msg = f"{msg}\n SN= {model.sn}"
                msg = f"{msg}\n 비활성화 하면 활성화를 못할 수 있습니다."
            return "sensor-update", msg, no_update, no_update
        else:
            # 소유 그룹이 바뀌지 않는 경우 -> 확인없이 업데이트 진행
            return "sensor-update", "", 1 + (0 if not nSubmit else nSubmit), no_update
            
    except AdminError as ex:
        return no_update, no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Output({"admin-manage-status-label": "sensor"}, "data"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-confirm", "trigger"),
    State("admin-manage-sensor", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    State("admin-manage-sensor-location", "value"),
    State("admin-manage-sensor-active", "value"),
    prevent_initial_call=True,
)
def onUpdateConfirmed(n, src, id, name, sn, locId, active):
    """<Update> 작업 및 목록 업데이트"""

    if not n or src != "sensor-update":
        return no_update

    try:
        model: Sensor = Sensor.query.get(id)
        if model == None:
            raise AdminError("삭제됨 - 존재하지 않는 레코드")
        model.name = name
        model.location_id = locId
        model.sn = sn

        newActive = len(active) > 0
        err = model.activate(newActive)
        if err:
            raise AdminError(err)

        dba = fl.g.dba
        dba.session.commit()
        return *buildSensorOptions(model.group_id, id), ["업데이트 완료", cnOk]

    except AdminError as ex:
        return *buildSensorOptions(model.group_id, id), [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Output({"admin-manage-status-label": "sensor"}, "data"),
    Input("admin-manage-sensor-delete", "n_clicks"),
    State("admin-manage-sensor", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, id):
    """<Delete> 버튼 확인 대화상자"""

    if not n or not id:
        return no_update

    try:
        model: Sensor = Sensor.query.get(id)
        if model == None:
            raise AdminError("삭제됨 - 존재하지 않는 레코드")

        numRows = sd.Count(sensor_id=id)
        # numRows = db.execute(sql).fetchone()[0]
        # numRows = next(iter(numRows.fetchone() or []), None)
        msg = f"센서를 삭제하면 센서의 측정데이터 <{numRows}>개도 모두 삭제됩니다."
        msg = f"{msg}\n\n센서 {model}를 삭제할까요?"
        return "sensor-delete", msg, no_update

    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Output({"admin-manage-status-label": "sensor"}, "data"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-confirm", "trigger"),
    State("admin-manage-sensor", "value"),
    prevent_initial_call=True,
)
def onDeleteConfirmed(n, src, id):
    """<Delete> 버튼 작업 - 센서 삭제, 센서데이터가 있으면 삭제 안함"""

    if not n or src != "sensor-delete":
        return no_update

    try:
        model: Sensor = Sensor.query.get(id)
        if model == None:
            raise AdminError("삭제됨 - 존재하지 않는 레코드")

        # 데이터 삭제
        user: AppUser = fli.current_user
        if user.is_master() or user.is_gadmin():
            sd.f1_clear_data(id)

        # 센서 삭제
        db = fl.g.dba.session
        db.delete(model)
        db.commit()
        return *buildSensorOptions(model.group_id), [f"{model} 삭제 완료", cnOk]

    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]
