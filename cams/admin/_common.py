"""패키지 admin 에서 공통으로 사용하는 함수"""

from ._imports import *
# from dash import html
# from dash import dcc


def buildButtonRow(buttonText, modelName, showUpdateIcon: bool = True):
    """추가 항목에 사용할 버튼 생성
      + HTML IDs:
        - admin-manage-save-{modelName}   : save icon
        - admin-manage-button-{modelName} : add new button 
        - data-model="{modelName}"        : button data-* property
    """

    icon = html.Span(
        "save",
        className="material-icons-outlined",
        id=f"admin-manage-save-{modelName}",
        n_clicks=0,
    )

    return html.Div(
        [
            html.Span("_", className="material-icons-two-tone"),
            html.Span("_", className="material-icons-two-tone"),
            html.Button(
                [
                    html.Span(
                        "add_circle_outline", className="material-icons-outlined"
                    ),
                    html.Span(buttonText, className="font-sc"),
                ],
                id=f"admin-manage-button-{modelName}",
                n_clicks=0,
                **{f"data-model": modelName},
            ),
            icon if showUpdateIcon else "",
        ],
        className="admin-manage-label",
    )


def buildUserOptions():
    """AppUser dropdown에 사용할 목록"""

    user: AppUser = fli.current_user
    if user.level >= 2:
        # 마스터 계정인 경우 - 모든 사용자 관리
        users = AppUser.query.all()
    elif user.level == 1:
        # 그룹 관리자 계정 경우 - 소속 그룹 사용자 관리
        users = AppUser.query.filter_by(group_id=user.group_id)
    else:
        # 일반 계정 경우 - 로그인한 사용자 자신만 관리
        users = [user]
    options = [{"label": u.username, "value": u.id} for u in users]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, default


def buildLocationOptions(uid, selected=None):
    """Location dropdown에 사용할 목록"""

    user = AppUser.query.get(uid)
    farms = user.group.locations
    options = [{"label": f.name, "value": f.id} for f in farms]
    default = options[0]["value"] if len(options) > 0 else ""
    if selected:
        default = selected
    return options, default


def buildSensorOptions(uid, selected=None):
    """Sensor dropdown에 사용할 목록"""

    user = AppUser.query.get(uid)
    sensors = user.group.sensors
    options = [{"label": s.name, "value": s.id} for s in sensors]
    default = options[0]["value"] if len(options) > 0 else ""
    if selected:
        default = selected
    return options, default


def buildInputLabel(
    labelText, modelName, colName, value, maxLen, readonly: bool = False, addId=False
):
    """html.Input을 포함한 html.Label 생성"""

    return html.Label(
        [
            html.Span(labelText),
            html.Span("_", className="material-icons-two-tone"),
            dcc.Input(
                id=f"admin-manage-{modelName}-{colName}",
                type="text",
                value=value,
                maxLength=maxLen,
                required=True,
                readOnly=readonly,
            ),
        ],
        className="admin-manage-label",
        id=f"admin-manage-{modelName}-{colName}-label",
    )
