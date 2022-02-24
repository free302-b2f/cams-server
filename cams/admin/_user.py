"""사용자 정보 변경 화면"""

from ._common import *
from dash.dependencies import Input, Output, State


def buildUserSection():
    """AppUser의 빈 목록 및 편집 섹션 생성"""

    # calc permissions
    user: AppUser = fli.current_user
    isMaster, isGAdmin, isNormal, isGuest = user.is_levels()
    canAdd = False
    canUpdate = isMaster or isGAdmin or isNormal or isGuest
    canDelete = isMaster or isGAdmin
    showGroup = isMaster
    showLevel = isMaster or isGAdmin

    list = buildLabel_Dropdown(
        "이용자 관리",
        "user",
        None,
        # *buildUserOptions(),
        [],
        None,
        "badge",
        [("clear", "delete")] if canDelete else None,
    )

    return html.Section(
        [
            html.Hr(),
            list,
            # buildLabel_Dropdown("Group", "user", "group", *buildGroupOptions()),
            buildLabel_Dropdown(
                "Group", "user", "group", [], None, hidden=not showGroup
            ),
            buildLabel_Input(
                "Login ID", "user", "username", "", AppUser.max_username, True
            ),
            buildLabel_Input(
                "Email", "user", "email", "", AppUser.max_email, not canUpdate
            ),
            buildLabel_Input(
                "Real Name", "user", "realname", "", AppUser.max_realname, not canUpdate
            ),
            buildLabel_Dropdown(
                "Level", "user", "level", [], None, hidden=not showLevel
            ),
            buildButtonRow("user", canAdd, hidden=not canUpdate),
        ],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-user", "options"),
    Output("admin-manage-user", "value"),
    Input("admin-manage-user-save", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-user-group", "value"),
    State("admin-manage-user-email", "value"),
    State("admin-manage-user-realname", "value"),
    State("admin-manage-user-level", "value"),
    prevent_initial_call=True,
)
def onUpdateClick(n, uid, gid, email, realname, level):
    """<Update> 버튼 작업 및 목록 업데이트"""

    if not n or not uid:
        return no_update

    try:
        dba = fl.g.dba
        model: AppUser = AppUser.query.get(uid)
        if model == None:
            return no_update

        gidOld = model.group_id
        model.group_id = gid

        model.email = email
        model.realname = realname

        # level
        if model.is_master() and level != AppUser.level_master:
            num = AppUser.query.filter_by(level=AppUser.level_master).count()
            if num >= 2:
                model.set_level(level)
        elif model.is_gadmin() and level != AppUser.level_group_admin:
            num = AppUser.query.filter_by(level=AppUser.level_group_admin).count()
            if num >= 2:
                model.set_level(level)
        else:
            model.set_level(level)

        dba.session.commit()
        return buildUserOptions(gidOld, uid)  # update model list
    except:
        return no_update


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Input("admin-manage-user-delete", "n_clicks"),
    State("admin-manage-user", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, uid):
    """<Delete> 버튼 확인 대화상자"""

    if not n or not uid:
        return no_update

    masters = AppUser.query.filter_by(level=AppUser.level_master)
    if uid in [u.id for u in masters]:
        return no_update

    model: AppUser = AppUser.query.get(uid)
    msg = f"사용자 <{model}> 계정을 삭제할까요?"
    return "user", msg


@app.callback(
    Output("admin-manage-user", "options"),
    Output("admin-manage-user", "value"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-confirm", "trigger"),
    State("admin-manage-user", "value"),
    prevent_initial_call=True,
)
def onDeleteConfirmed(n, src, uid):
    """<Delete> 버튼 작업 - 마스터만 삭제 가능"""

    if not n or src != "user":
        return no_update

    try:
        # 모델 존재 체크
        model: AppUser = AppUser.query.get(uid)
        if model == None:
            return no_update

        # 현재 로그인 사용자 삭제 불가
        user: AppUser = fli.current_user
        if model.id == user.id:
            return no_update

        gid = model.group_id
        dba = fl.g.dba
        if user.is_master():
            dba.session.delete(model)
        elif user.is_gadmin():
            model.set_deleted()

        dba.session.commit()
        return buildUserOptions(gid)
    except:
        return no_update
