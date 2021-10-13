"""패키지 admin 에서 공통으로 사용하는 함수"""

from admin._imports import *

g_users: List[AppUser] = AppUser.query.all()
g_farms: List[Farm] = None
g_sensors: List[Sensor] = None


def buildButtonRow(buttonText, modelName):
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

    global g_users, g_farms, g_sensors

    g_users = AppUser.query.all()
    options = [{"label": u.username, "value": u.id} for u in g_users]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, default


def buildFarmOptions(uid, selected=None):
    """Farm dropdown에 사용할 목록"""

    global g_users, g_farms, g_sensors

    user = AppUser.query.get(uid)
    g_farms = user.farms
    options = [{"label": f.name, "value": f.id} for f in g_farms]
    default = options[0]["value"] if len(options) > 0 else ""
    if selected:
        default = selected
    return options, default



def buildSensorOptions(fid):
    """Sensor dropdown에 사용할 목록"""

    global g_users, g_farms, g_sensors

    farm = Farm.query.get(fid)
    g_sensors = farm.sensors
    options = [{"label": s.name, "value": s.id} for s in g_sensors]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, default




