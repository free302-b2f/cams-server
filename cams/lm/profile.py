"""로그인한 사용자의 프로파일 뷰 및 콜백"""

print(f"<{__name__}> loading...")

from lm._imports import *
import lm.logout

from db.user import AppUser
from db.location import Location
from db.sensor import Sensor

from app import app, addPage
from dash import no_update
from apps._imports import *

_userMaxLen = AppUser.max_len()


def _action_icon(name: str, id: int, add: bool):
    """편집,삭제 아이콘 생성"""

    list = html.Span(
        [
            html.Span(
                "edit",
                className="material-icons-outlined",
                id={"model": f"edit-{name}", "id": id},
                n_clicks=0,
                **{f"data-{name}_id": id},
            ),
            html.Span(
                "save",
                className="material-icons-outlined",
                id={"model": f"save-{name}", "id": id},
                n_clicks=0,
                **{f"data-{name}_id": id},
            ),
            html.Span(
                "delete",
                className="material-icons-outlined",
                id={"model": f"delete-{name}", "id": id},
                n_clicks=0,
                **{f"data-{name}_id": id},
            ),
        ]
    )
    if add:
        list.children.append(
            html.Span(
                "add_circle_outline",
                className="material-icons-outlined",
                id={"model": f"add-{name}", "id": id},
                n_clicks=0,
                **{f"data-{name}_id": id},
            ),
        )
    return list


def buildPersonalLabel(labelText, userName, colName):
    return html.Label(
        [
            html.Span(labelText),
            dcc.Input(
                id=f"lm-profile-personal-{colName}",
                type="text",
                value=userName,
                maxLength=_userMaxLen[f"max_{colName}"],
                required=True,
                readOnly=True,
            ),
            html.Span("", className="material-icons-outlined"),
        ]
    )


def buildLocationLabel(index, location: Location):
    return html.Label(
        [
            html.Span(f"Location {index}"),
            dcc.Input(
                # id=f"lm-profile-farms-{id}",
                id={"model": "farm", "id": location.id},
                type="text",
                value=f"{location.id}: {location.name}",
                maxLength=Location.max_name,
                required=True,
                readOnly=True,
            ),
            # _action_icon("farm", id, True),
        ]
    )


def buildSensorLabel(index, sensor: Sensor):
    return html.Label(
        [
            html.Span(f"Sensor {index}"),
            dcc.Input(
                id=f"lm-profile-sensors-{id}",
                type="text",
                value=f"{sensor.id}: {sensor.name}",
                maxLength=Sensor.max_sn + 5,
                required=True,
                readOnly=True,
            ),
            # _action_icon("sensor", id, False),
        ]
    )


def layout():

    user: AppUser = fli.current_user
    if user == None or not user.is_authenticated:
        return html.Div()

    locations = user.group.locations
    sensors = user.group.sensors

    _header = html.Header(
        [
            html.H5(
                [
                    html.Span("manage_accounts", className="material-icons-two-tone"),
                    html.Span(
                        f"{user.username} : {user.realname}", className="font-sc"
                    ),  # "User Account",
                ],
                className="flex-h",
            ),
        ],
        id="lm-profile-header",
    )
    _menu = html.Section(
        [
            html.A(  # dcc.Link:
                [
                    html.Span("Change"),
                    html.Span("password", className="material-icons-two-tone"),
                ],
                href="/change",
                className="flex-h mr1",
            ),
            *(lm.logout.layout),
        ],
        className="flex-h-right",
        id="lm-profile-menu",
    )

    _profile = html.Section(
        [
            html.H5(
                [
                    html.Span("badge", className="material-icons-two-tone"),
                    "Personal Profile",
                    dcc.Link(
                        html.Span(
                            "edit",
                            className="material-icons-outlined",
                        ),
                        href="/admin-manage",
                    ),
                ],
                className="flex-h",
            ),
            buildPersonalLabel("Login ID", user.username, "username"),
            buildPersonalLabel("Email", user.email, "email"),
            buildPersonalLabel("Real Name", user.realname, "realname"),
        ],
        id="lm-profile-personal",
        className="flex-v",
    )

    _locations = html.Section(
        [
            html.H5(
                [
                    html.Span("yard", className="material-icons-two-tone"),
                    "Location List",
                    dcc.Link(
                        html.Span(
                            "edit",
                            className="material-icons-outlined",
                        ),
                        href="/admin-manage",
                    ),
                ],
                className="flex-h",
            ),
            *[buildLocationLabel(i, f) for i, f in enumerate(locations, 1)],
        ],
        id="lm-profile-farms",
        className="flex-v",
    )

    _sensors = html.Section(
        [
            html.H5(
                [
                    html.Span("sensors", className="material-icons-two-tone"),
                    "Sensor List",
                    dcc.Link(
                        html.Span(
                            "edit",
                            className="material-icons-outlined",
                        ),
                        href="/admin-manage",
                    ),
                ],
                className="flex-h",
            ),
            *[buildSensorLabel(i, s) for i, s in enumerate(sensors, 1)],
        ],
        id="lm-profile-sensors",
        className="flex-v",
    )

    _settings = html.Section(
        [
            html.H5(
                [
                    html.Span("settings", className="material-icons-two-tone"),
                    "Preference",
                ],
                className="flex-h",
            ),
            html.Pre(" - 사용자 설정 사항..."),
        ],
        id="lm-profile-preference",
        className="flex-v",
    )

    _security = html.Section(
        [
            html.H5(
                [
                    html.Span("security", className="material-icons-two-tone"),
                    "Activity Log",
                ],
                className="flex-h",
            ),
            html.Pre(" - 활동/보안 기록..."),
        ],
        id="lm-profile-security",
        className="flex-v",
    )

    return html.Div(
        [
            _header,
            _menu,
            _profile,
            _sensors,
            _locations,
            _settings,
            _security,
            dcc.Location(id="lm-profile-url", refresh=True),
            html.Div(id="lm-profile-status", className="text-danger", n_clicks=0),
        ],
        id="lm-profile-container",
        className="content-pad",
    )


# @app.callback(
#     Output("lm-profile-url", "pathname"),
#     Input("lm-profile-personal-edit", "n_clicks"),
#     Input("lm-profile-location-edit", "n_clicks"),
#     Input("lm-profile-sensor-edit", "n_clicks"),
#     prevent_initial_call=True,
# )
# def onEditClick(n1, n2, n3):

#     # if n1 or n2 or n3:
#     #     return "/admin-manage"

#     return no_update


# 이 페이지를 메인 라우터에 등록한다.
addPage(layout)
