"""그룹 관리 화면"""

from ._common import *
import sys
from dash.dependencies import Input, Output, State
from db import sensor_data as sd

# className for status span


def buildGroupSection():
    """그룹 목록과 편집 섹션 생성"""

    # calc permissions
    user: AppUser = fli.current_user
    isMaster, isGAdmin, _, _ = user.is_levels()
    canAdd = isMaster
    canUpdate = isMaster or isGAdmin
    canDelete = isMaster
    hideSection = not isMaster and not isGAdmin

    list = buildLabel_Dropdown(
        "그룹 관리",
        "group",
        None,
        *buildGroupOptions(),
        "groups",
        [("clear", "delete")] if canDelete else None,
    )

    name = buildLabel_Input(
        "Group Name", "group", "name", "", Group.max_name, not canUpdate
    )
    desc = buildLabel_Input(
        "Description", "group", "desc", "", Group.max_desc, not canUpdate
    )
    button = buildButtonRow("group", canAdd, not canUpdate)
    status = buildStatusRow("group")

    section = html.Section(
        [list, name, desc, button, status],
        className="admin-manage-edit-section",
        style={"display": "none"} if hideSection else {},
        id={"admin-manage-section": "group"},
    )
    section.data = []  #
    return section


@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Output({"admin-manage-status-label": "group"}, "data"),
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
        return *buildGroupOptions(model.id), [f"{model} 추가 완료", cnOk]
        
    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Output({"admin-manage-status-label": "group"}, "data"),
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
            raise AdminError("삭제됨 - 존재하지 않는 레코드")

        model.name = name
        model.desc = desc
        dba.session.commit()
        return *buildGroupOptions(gid), ["업데이트 완료", cnOk]

    except AdminError as ex:
        return *buildGroupOptions(gid), [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Output({"admin-manage-status-label": "group"}, "data"),
    Input("admin-manage-group-delete", "n_clicks"),
    State("admin-manage-group", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, gid):
    """<Delete> 버튼 확인 대화상자"""

    if not n or gid is None:
        return no_update

    try:
        model: Group = Group.query.get(gid)
        numRows = sd.Count(gid)
        msg = f"그룹 <{model}>을 삭제할까요?"
        msg = f"{msg}\n\n그룹을 삭제하면 그룹소속 다음 데이터도 함께 삭제됩니다."
        msg = f"{msg}\n - 사용자: {len(model.users)}개"
        msg = f"{msg}\n - 위치: {len(model.locations)}개"
        msg = f"{msg}\n - 센서: {len(model.sensors)}개"
        msg = f"{msg}\n - 센서데이터: {numRows}개"
        return "group", msg, no_update

    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-group", "options"),
    Output("admin-manage-group", "value"),
    Output({"admin-manage-status-label": "group"}, "data"),
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
            return *buildGroupOptions(), ["삭제됨 - 존재하지 않는 레코드", cnError]

        user: AppUser = fli.current_user
        if model.id == user.group_id:
            raise AdminError("삭제불가 - 현재 로그인한 사용자의 그룹")

        dba = fl.g.dba
        if user.is_master():
            [sd.f1_clear_data(x.id) for x in model.sensors]
            # Sensor.query.filter_by(group_id = model.id).delete()
            [dba.session.delete(x) for x in model.sensors]
            [dba.session.delete(x) for x in model.locations]
            [dba.session.delete(x) for x in model.users]

        dba.session.delete(model)
        dba.session.commit()

        return *buildGroupOptions(), [f"삭제완료: {model}", cnOk]

    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]