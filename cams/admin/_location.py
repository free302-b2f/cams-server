"""위치 추가 화면"""

from ._common import *
from dash.dependencies import Input, Output, State
from db import sensor_data as sd


def buildLocationSection():
    """Location의 빈 목록 및 편집 섹션을 생성"""

    user: AppUser = fli.current_user
    isMaster, isGAdmin, isNormal = user.is_levels()
    canDelete = isMaster
    canUpdate = isMaster or isGAdmin or isNormal
    canAdd = isMaster or isGAdmin or isNormal

    list = buildLabel_Dropdown(
        "Location",
        "location",
        None,
        [],
        None,
        "yard",
        [("clear", "delete")] if canDelete else None,
    )
    name = buildLabel_Input(
        "Name", "location", "name", "", Location.max_name, not canUpdate
    )
    desc = buildLabel_Input(
        "Description", "location", "desc", "", Location.max_desc, not canUpdate
    )
    button = buildButtonRow("location", canAdd, not canUpdate)

    return html.Section(
        [html.Hr(), list, name, desc, button],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-location-add", "n_clicks"),
    State("admin-manage-group", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onAddClick(n, gid, name, desc):
    """<Add> 버튼 작업 및 위치 목록 업데이트"""

    if not n:
        return no_update

    location: Location = Location(name=name, desc=desc, group_id=gid)

    try:
        db = fl.g.dba.session
        db.add(location)
        db.commit()
        return buildLocationOptions(gid, location.id)
    except:
        return no_update


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-location-save", "n_clicks"),
    State("admin-manage-group", "value"),
    State("admin-manage-location", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onUpdateClick(n, gid, id, name, desc):
    """<Update> 버튼 작업 및 목록 업데이트"""

    if not n:
        return no_update

    try:
        model: Location = Location.query.get(id)
        if model == None:
            return no_update

        model.name = name
        model.desc = desc
        fl.g.dba.session.commit()
        return buildLocationOptions(gid, id)
    except:
        return no_update


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Input("admin-manage-location-delete", "n_clicks"),
    State("admin-manage-location", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, id):
    """<Delete> 버튼 확인 대화상자"""

    if not n or not id:
        return no_update

    model: Location = Location.query.get(id)
    if model != None:
        return no_update

    msg = f"위치를 삭제하면 위치에 연관된 센서데이터도 모두 삭제됩니다."
    msg = f"{msg}\n\n위치 <{model.id}:{model}>를 삭제할까요?"
    return "location", msg


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-confirm", "trigger"),
    State("admin-manage-location", "value"),
    prevent_initial_call=True,
)
def onDeleteConfirmed(n, src, id):
    """<Delete> 버튼 작업 - 위치 삭제, 연결되 센서/센서데이터가 있으면 삭제 안함"""

    if not n or src != "location":
        return no_update

    try:
        model: Location = Location.query.get(id)
        if model == None:
            return no_update

        group: Group = model.group
        user: AppUser = fli.current_user

        # 센서를 현재 위치에서 보관소로 이동
        for s in model.sensors:
            s.location_id = group.storage_id

        # 데이터 삭제
        if user.is_master():
            sd.f1_clear_location_data(model.id)

        db = fl.g.dba.session
        db.delete(model)
        db.commit()
        return buildLocationOptions(group.id)
    except:
        return no_update
