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
            # html.Hr(),
            list,
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
            buildStatusRow("user"),
        ],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-user", "options"),
    Output("admin-manage-user", "value"),
    Output({"admin-manage-status-label": "user"}, "data"),
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
            raise AdminError("삭제됨 - 존재하지 않는 레코드")

        model.email = email
        model.realname = realname

        gidOld = model.group_id
        if model.is_gadmin() and gidOld != gid:
            num = AppUser.query.filter_by(
                level=AppUser.level_group_admin, group_id=gidOld
            ).count()
            if num <= 1:
                raise AdminError("마지막 그룹관리자 계정은 다른 그룹으로 변경할 수 없습니다.")
        model.group_id = gid

        # 마스터 계정 변경
        if model.is_master() and level != AppUser.level_master:
            num = AppUser.query.filter_by(level=AppUser.level_master).count()
            if num <= 1:
                raise AdminError("마지막 마스터 계정은 다른 계정으로 변경할 수 없습니다.")
        # 그룹관리자 변경
        elif model.is_gadmin() and level != AppUser.level_group_admin:
            num = AppUser.query.filter_by(
                level=AppUser.level_group_admin, group_id=gidOld
            ).count()
            if num <= 1:
                raise AdminError("마지막 그룹관리자 계정은 다른 계정으로 변경할 수 없습니다.")
        model.set_level(level)

        dba.session.commit()
        return *buildUserOptions(gidOld, uid), ["업데이트 완료", cnOk]

    except AdminError as ex:
        return *buildUserOptions(gidOld, uid), [f"에러:{ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Output({"admin-manage-status-label": "user"}, "data"),
    Input("admin-manage-user-delete", "n_clicks"),
    State("admin-manage-user", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, uid):
    """<Delete> 버튼 확인 대화상자"""

    if not n or not uid:
        return no_update

    try:
        # 모델 존재 체크
        model: AppUser = AppUser.query.get(uid)
        if model == None:
            raise AdminError("삭제됨 - 존재하지 않는 레코드")

        if model.is_master():
            runRows = AppUser.query.filter_by(level=AppUser.level_master).count()
            if runRows < 2:
                raise AdminError("마지막 마스터 계정은 삭제할 수 없습니다.")

        model: AppUser = AppUser.query.get(uid)
        msg = f"사용자 <{model}> 계정을 삭제할까요?"
        return "user", msg, no_update

    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]

@app.callback(
    Output("admin-manage-user", "options"),
    Output("admin-manage-user", "value"),
    Output({"admin-manage-status-label": "user"}, "data"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-confirm", "trigger"),
    State("admin-manage-user", "value"),
    State("admin-manage-group", "value"),
    prevent_initial_call=True,
)
def onDeleteConfirmed(n, src, uid, gid):
    """<Delete> 버튼 작업 - 마스터만 삭제 가능"""

    if not n or src != "user":
        return no_update

    try:
        # 모델 존재 체크
        model: AppUser = AppUser.query.get(uid)
        if model == None:
            return *buildUserOptions(gid), ["삭제됨 - 존재하지 않는 레코드", cnError]

        # 현재 로그인 사용자 - 삭제 불가
        user: AppUser = fli.current_user
        if model.id == user.id:
            return no_update, no_update, ["에러발생 - ", cnError]

        # 마지막 그룹 관리자 - 삭제 불가
        if model.is_gadmin():
            numRows = AppUser.query.filter_by(
                level=AppUser.level_group_admin, group_id=gid
            ).count()
            if numRows < 2:
                return no_update, no_update, ["마지막 마스터 계정은 삭제할 수 없습니다.", cnError]

        dba = fl.g.dba
        if user.is_master():
            dba.session.delete(model)
        elif user.is_gadmin():
            model.set_deleted()

        dba.session.commit()
        return *buildUserOptions(gid), [f"삭제완료: {model}", cnOk]

    except AdminError as ex:
        return *buildUserOptions(gid), [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]