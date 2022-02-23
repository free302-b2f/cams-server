"""그룹 관리 화면"""

from ._common import *
import sys
from dash.dependencies import Input, Output, State
from db import sensor_data as sd


def buildGroupSection():
    """그룹 목록과 편집 섹션 생성"""

    user: AppUser = fli.current_user
    isMaster = user.is_master()
    isGAdmin = user.is_gadmin()
    hidden = not isMaster and not isGAdmin

    list = buildLabel_Dropdown(
        "Group",
        "group",
        None,
        *buildGroupOptions(),
        "groups",
        [("clear", "delete")] if isMaster else None,
    )

    name = buildLabel_Input("Group Name", "group", "name", "", Group.max_name)
    desc = buildLabel_Input("Description", "group", "desc", "", Group.max_desc)
    button = buildButtonRow("group", isMaster)
    hiddenStyle = {"display": "none"} if hidden else {}

    return html.Section(
        [list, name, desc, button],
        className="admin-manage-edit-section",
        style=hiddenStyle,
    )


@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Input("admin-manage-group-add", "n_clicks"),
    State("admin-manage-group-name", "value"),
    State("admin-manage-group-desc", "value"),
    prevent_initial_call=True,
)
def onAddClick(n, name, desc):
    """<Add> 버튼 작업 및 Group 목록 업데이트"""

    if not n:  # prevent_initial_call=True이더라도 리로드시 n=0로 호출됨
        return no_update

    try:
        dba = fl.g.dba
        model = Group(name=name, desc=desc)        
        dba.session.add(model)
        dba.session.commit()
        return buildGroupOptions(model.id)
    except:
        return no_update


@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Input("admin-manage-group-save", "n_clicks"),
    State("admin-manage-group", "value"),
    State("admin-manage-group-name", "value"),
    State("admin-manage-group-desc", "value"),
    prevent_initial_call=True,
)
def onUpdateClick(n, gid, name, desc):
    """<Update> 버튼 작업 및 목록 업데이트"""

    if not n:
        return no_update

    try:
        dba = fl.g.dba
        model = Group.query.get(gid)
        if model == None:
            return no_update

        model.name = name
        model.desc = desc
        dba.session.commit()
        return buildGroupOptions(gid)
    except:
        return no_update


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Input("admin-manage-group-delete", "n_clicks"),
    State("admin-manage-group", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, gid):
    """<Delete> 버튼 확인 대화상자"""

    if not n or not gid:
        return no_update

    model: Group = Group.query.get(gid)
    msg = f"그룹을 삭제하면 그룹소속 모든 사용자/위치/센서/측정데이터가 삭제됩니다."
    msg = f"{msg}\n\n그룹 <{model}>을 삭제할까요?"
    return "group", msg



@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-confirm", "trigger"),
    State("admin-manage-group", "value"),
    prevent_initial_call=True,
)
def onDeleteConfirmed(n, src, gid):
    """<Delete> 버튼 작업 - 마스터만 삭제 가능"""

    if not n or src != "group":
        return no_update

    try:
        model: Group = Group.query.get(gid)
        if model == None:
            return no_update

        user: AppUser = fli.current_user

        if not getattr(sys, "_test_"):
            if model.id == user.group_id:
                return no_update

        dba = fl.g.dba
        if user.is_master():
            [sd.f1_clear_data(x.id) for x in model.sensors]
            # Sensor.query.filter_by(group_id = model.id).delete()
            [dba.session.delete(x) for x in model.sensors]
            [dba.session.delete(x) for x in model.locations]
            [dba.session.delete(x) for x in model.users]

        dba.session.delete(model)
        dba.session.commit()
    except:
        return no_update

    # update model list
    return buildGroupOptions()
