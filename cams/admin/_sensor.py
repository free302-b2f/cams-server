"""센서 추가 화면"""

from ._common import *
from dash.dependencies import Input, Output, State
from db import sensor_data as sd


def buildSensorSection():
    """Sensor의 빈 목록 및 편집 섹션을 생성"""

    # calc permissions
    user: AppUser = fli.current_user
    isMaster, isGAdmin, isNormal, _ = user.is_levels()
    canAdd = isMaster or isGAdmin
    canUpdate = isMaster or isGAdmin or isNormal
    canDelete = isMaster or isGAdmin

    list = buildLabel_Dropdown(
        "센서 관리",
        "sensor",
        None,
        [],
        None,
        "sensors",
        [("clear", "delete")] if canDelete else None,
    )
    name = buildLabel_Input(
        "Sensor Name", "sensor", "name", "", Sensor.max_name, not canUpdate
    )
    sn = buildLabel_Input("Sensor SN", "sensor", "sn", "", Sensor.max_sn, not canDelete)
    locs = buildLabel_Dropdown(
        "Location", "sensor", "location", [], None, "", hidden=not canUpdate
    )
    button = buildButtonRow("sensor", canAdd, not canUpdate)

    return html.Section(
        [html.Hr(), list, name, sn, locs, button],
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
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-sensor-save", "n_clicks"),
    State("admin-manage-sensor", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    State("admin-manage-sensor-location", "value"),
    prevent_initial_call=True,
)
def onUpdateClick(n, id, name, sn, locId):
    """<Update> 버튼 작업 및 목록 업데이트"""

    if not n:
        return no_update

    try:
        model: Sensor = Sensor.query.get(id)
        model.name = name
        model.sn = sn
        model.location_id = locId

        dba = fl.g.dba
        dba.session.commit()
        return buildSensorOptions(model.group_id, id)
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
