"""로그인한 사용자의 프로파일 뷰 및 콜백"""

from dash_html_components.Br import Br
from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app, add_page
import lm.logout


def layout():

    user = fli.current_user
    userId = fli.current_user.get_id()

    sectionStyle = {"margin-top": "20px", "margin-bottom": "10px"}

    _header = html.Header(
        [
            html.H4(
                [
                    html.Span("manage_accounts", className="material-icons-two-tone"),
                    "User Account",
                ],
                className="flex-horizontal",
            ),
        ],
        className="lm-profile-header",
    )
    _menu = html.Section(
        [
            *(lm.logout.layout),
            # <span class="material-icons-two-tone">password</span>
            dcc.Link(
                [
                    "Change Password",
                    html.Span("password", className="material-icons-two-tone"),
                ],
                href="lm.change",
                className="flex-horizontal",
            ),
        ],
        className="flex-horizontal",
    )

    _profile = html.Section(
        [
            html.H5("Personal Profile"),
            html.Label("Login ID", htmlFor="lm-profile-username"),
            dcc.Input(
                id="lm-profile-username",
                type="text",
                value=user.username,
                maxLength=db.User.max_username,
                required=True,
                readOnly=True,
            ),
            html.Br(),
            html.Label("Email", htmlFor="lm-profile-email"),
            dcc.Input(
                id="lm-profile-email",
                type="email",
                value=user.email,
                maxLength=db.User.max_email,
                required=True,
                readOnly=True,
            ),
        ]
    )

    return html.Div(
        [
            _header,
            _menu,
            _profile,
            dcc.Location(id="lm-profile-url", refresh=True),
            html.Br(),
            dbc.Button("Edit/Save"),
            html.H3("Preference", style=sectionStyle),
            html.Pre(" - 사용자 옵션..."),
            dbc.Button("Edit/Save"),
            html.H3("Farms", style=sectionStyle),
            html.Pre(" - 로그인한 사용자가 관리하는 농장 목록"),
            html.H3("Sensors", style=sectionStyle),
            html.Pre(" - 로그인한 사용자가 관리하는 센서/장비 목록"),
            html.H3("Log", style=sectionStyle),
            html.Pre(" - 보안/기술적인 기록"),
            html.Div(id="lm-profile-status", className="text-danger"),
        ],
        id="lm-profile-container",
    )


# 이 페이지를 메인 라우터에 등록한다.
# add_page(layout, "Log In")  # test
add_page(layout)  # test
