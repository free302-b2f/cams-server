"""그룹 관리 화면"""

from ._common import *
from dash.dependencies import Input, Output, State
from db import sensor_data as sd


def buildGroupSection():
    """그룹 목록과 편집 섹션 생성"""

    user: AppUser = fli.current_user
    isMaster = user.is_master()
    readOnly = not user.is_master() and not user.is_gadmin()

    list = buildLabel_Dropdown(
        "Group",
        "group",
        None,
        *buildGroupOptions(),
        "groups",
        [("clear", "delete")] if isMaster else None,
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
    Input("admin-manage-group-button", "n_clicks"),
    State("admin-manage-group-name", "value"),
    State("admin-manage-group-desc", "value"),
    prevent_initial_call=True,
)
def onNewClick(n, name, desc):
    """<Add> 버튼 작업 및 Group 목록 업데이트"""

    if not n:  # prevent_initial_call=True이더라도 리로드시 n=0로 호출됨
        return no_update

    try:
        dba = fl.g.dba
        model = Group(name=name, desc=desc)
        dba.session.add(model)
        dba.session.commit()
    except:
        return no_update

    # update model list
    return buildGroupOptions(model.id)


@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Input("admin-manage-group-save", "n_clicks"),
    State("admin-manage-group", "value"),
    State("admin-manage-group-name", "value"),
    State("admin-manage-group-desc", "value"),
    prevent_initial_call=True,
)
def onSaveClick(n, gid, name, desc):
    """<Save> 버튼 작업 및 목록 업데이트"""

    if not n:
        return no_update

    try:
        dba = fl.g.dba
        model = Group.query.get(gid)
        model.name = name
        model.desc = desc
        dba.session.commit()
    except:
        return no_update

    # update model list
    return buildGroupOptions(model.id)


@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Input("admin-manage-group-delete", "n_clicks"),
    State("admin-manage-group", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, gid):
    """<Delete> 버튼 작업 - 센서 삭제, 센서데이터가 있으면 삭제 안함"""

    if not n:
        return no_update

    try:
        model = Group.query.get(gid)
        if model == None:
            return no_update

        user: AppUser = fli.current_user
        # if model.id == user.group_id:
        #     return no_update

        dba = fl.g.dba
        if user.is_master():
            [sd.f1_clear_data(x.id) for x in model.sensors]
            # dba.session.refresh()
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
