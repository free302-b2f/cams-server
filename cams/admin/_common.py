"""패키지 admin 에서 공통으로 사용하는 함수"""

from admin._imports import *


def buildButtonRow(buttonText, modelName):
    """추가 항목에 사용할 버튼 생성"""

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
        ],
        className="admin-manage-label",
    )


def buildUserOptions():
    """AppUser dropdown에 사용할 목록"""

    users = AppUser.query.all()
    options = [{"label": u.username, "value": u.id} for u in users]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, default


def buildFarmOptions(uid, selected=None):
    """Farm dropdown에 사용할 목록"""

    user = AppUser.query.get(uid)
    farms = user.farms
    options = [{"label": f.name, "value": f.id} for f in farms]
    default = options[0]["value"] if len(options) > 0 else ""
    if selected:
        default = selected
    return options, default


def buildSensorOptions(fid, selected=None):
    """Sensor dropdown에 사용할 목록"""

    farm = Farm.query.get(fid)
    sensors = farm.sensors
    options = [{"label": s.name, "value": s.id} for s in sensors]
    default = options[0]["value"] if len(options) > 0 else ""
    if selected:
        default = selected
    return options, default
