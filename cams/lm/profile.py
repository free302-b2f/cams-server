"""로그인한 사용자의 프로파일 뷰 및 콜백"""

from lm.imports import *
from db.user import AppUser
from db.farm import Farm
from db.sensor import Sensor

from app import app, add_page
import lm.logout


_userMaxLen = AppUser.max_len()


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


def buildFarmLabel(id: str, name: str) -> html.Label:
    return html.Label(
        [
            html.Span(f"Farm {id}"),
            dcc.Input(
                id=f"lm-profile-farms-{id}",
                type="text",
                value=name,
                maxLength=Farm.max_name,
                required=True,
                readOnly=True,
            ),
            html.Span("pageview", className="material-icons-outlined"),
        ]
    )


def buildSensorLabel(id: str, name: str) -> html.Label:
    return html.Label(
        [
            html.Span(f"Sensor {id}"),
            dcc.Input(
                id=f"lm-profile-sensors-{id}",
                type="text",
                value=name,
                maxLength=Sensor.max_sn + 5,
                required=True,
                readOnly=True,
            ),
            html.Span("play_arrow", className="material-icons-outlined"),
        ]
    )


def layout():

    user = fli.current_user
    userId = fli.current_user.get_id()
    farms = user.farms
    sensors = []
    for f in farms:
        sensors.extend(f.sensors)

    _header = html.Header(
        [
            html.H4(
                [
                    html.Span("manage_accounts", className="material-icons-two-tone"),
                    html.Span(user.realname, className="font-sc"),  # "User Account",
                ],
                className="flex-h",
            ),
        ],
        id="lm-profile-header",
    )
    _menu = html.Section(
        [
            dcc.Link(
                [
                    html.Span("Change"),
                    html.Span("password", className="material-icons-two-tone"),
                ],
                href="lm.change",
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
                    html.Span("edit", className="material-icons-outlined"),
                    # html.Span("save", className="material-icons-outlined"),
                ],
                className="flex-h",
            ),
            buildPersonalLabel("Login ID", user.username, "username"),
            buildPersonalLabel("Email", user.email, "email"),
            buildPersonalLabel("Real Name", user.realname, "realname"), 
            
            # html.Label(
            #     [
            #         html.Span(""),
            #         dbc.Button("Edit/Save"),
            #     ]
            # ),
        ],
        id="lm-profile-personal",
        className="flex-v",
    )

    _farms = html.Section(
        [
            html.H5(
                [
                    html.Span("yard", className="material-icons-two-tone"),
                    "Farm List",
                    html.Span("edit", className="material-icons-outlined"),
                ],
                className="flex-h",
            ),
            *[buildFarmLabel(f.id, f.name) for f in farms],
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
                    html.Span("edit", className="material-icons-outlined"),
                ],
                className="flex-h",
            ),
            *[buildSensorLabel(f.id, f.sn) for f in sensors],
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
                    "Acitvity Log",
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
            _farms,
            _sensors,
            _settings,
            _security,
            dcc.Location(id="lm-profile-url", refresh=True),
            html.Div(id="lm-profile-status", className="text-danger"),
        ],
        id="lm-profile-container",
        className="content-pad",
    )


# 이 페이지를 메인 라우터에 등록한다.
# add_page(layout, "Log In")  # test
add_page(layout)  # test
