"""그룹 관리 화면"""

from ._common import *
from dash.dependencies import Input, Output, State


def buildGroupSection():
    """그룹 목록과 편집 섹션 생성"""

    user:AppUser = fli.current_user
    isMaster = user.is_master()
    readOnly = not user.is_master() and not user.is_gadmin()

    list = buildLabel_Dropdown(
        "Group",
        "group",
        None,
        *buildGroupOptions(),
        "groups",
        [("clear", "clear")] if isMaster else None,
        # hidden=readOnly
    )

    name = buildLabel_Input(
        "Group Name", "group", "name", "", Group.max_name, readonly=readOnly
    )
    desc = buildLabel_Input(
        "Description", "group", "desc", "", Group.max_desc, readonly=readOnly
    )

    button = (
        buildButtonRow(
            "Add New Group" if isMaster else "Update Group",
            "group",
            isMaster,
        )
        if not readOnly
        else None
    )

    return html.Section(
        [list, name, desc, button],
        className="admin-manage-edit-section",
        style={"display": "none"} if readOnly else None,
    )


@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Input("admin-manage-button-group", "n_clicks"),
    State("admin-manage-group-name", "value"),
    State("admin-manage-group-desc", "value"),
    prevent_initial_call=True,
)
def onNewClick(n, name, desc):
    """<Add> 버튼 작업 및 Group 목록 업데이트"""

    if not n:
        return no_update

    group = Group(name=name, desc=desc)

    dba = fl.g.dba
    try:
        dba.session.add(group)
        dba.session.commit()
    except:
        return no_update

    # trigger user change
    return buildGroupOptions(group.id)


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-save-sensor", "n_clicks"),
    State("admin-manage-location", "value"),
    State("admin-manage-sensor", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    prevent_initial_call=True,
)
def onSaveClick(n, fid, sid, name, sn):
    """<Save> 버튼 작업 및 목록 업데이트"""

    if not n:
        return no_update

    dba = fl.g.dba
    try:
        sensor = Sensor.query.get(fid)
        sensor.name = name
        sensor.sn = sn
        dba.session.commit()
    except:
        return no_update

    # trigger user change
    return buildSensorOptions(fid, sid)


# admin-manage-sensor-clear
@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-sensor-clear", "n_clicks"),
    State("admin-manage-location", "value"),
    State("admin-manage-sensor", "value"),
    prevent_initial_call=True,
)
def onClearClick(n, fid, sid):
    """<Clear> 버튼 작업 - 센서 삭제, 센서데이터가 있으면 삭제 안함"""

    if not n:
        return no_update

    dba = fl.g.dba
    try:
        sensor = Sensor.query.get(sid)
        dba.session.delete(sensor)
        dba.session.commit()
    except:
        return no_update

    return buildSensorOptions(fid)
