"""로그인한 사용자의 프로파일 뷰 및 콜백"""

from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app, add_page


def layout():

    user = fli.current_user
    userId = fli.current_user.get_id()

    divStyle = {
        "display": "flex",
        "flex-direction": "row",
        "justify-content": "flex-start",
    }
    linkStyle = {"margin-right": "15px"}
    sectionStyle = {"margin-top": "20px", "margin-bottom": "10px"}
    labelStyle = {"width":"100px"}

    return html.Div(
        [
            html.H1("User Account"),
            dcc.Location(id="lm-profile-url", refresh=True),
            html.Div(
                [
                    dcc.Link("Logout", href="lm.logout", style=linkStyle),
                    dcc.Link("Change Password", href="lm.change", style=linkStyle),
                ],
                style=divStyle,
            ),
            html.H3("Profile", style=sectionStyle),
            html.Label("Login ID", htmlFor="lm-profile-username", style=labelStyle),
            dcc.Input(
                id="lm-profile-username",
                type="text",
                value=user.username,
                maxLength=db.User.max_username,
                required=True,
                readOnly=True,
            ),
            html.Br(),
            html.Label("Email", htmlFor="lm-profile-email", style=labelStyle),
            dcc.Input(
                id="lm-profile-email",
                type="email",
                value=user.email,
                maxLength=db.User.max_email,
                required=True,
                readOnly=True,
            ),
            html.Br(),
            dbc.Button("Edit/Save"),
            html.H3("Preference", style=sectionStyle),
            html.Li("사용자 옵션..."),
            dbc.Button("Edit/Save"),
            html.H3("Farms", style=sectionStyle),
            html.Li("로그인한 사용자가 관리하는 농장 목록"),
            html.H3("Log", style=sectionStyle),
            html.Li("보안/기술적인 기록"),
            html.Div(id="lm-profile-status", className="text-danger"),
        ]
    )


# 이 페이지를 메인 라우터에 등록한다.
# add_page(layout, "Log In")  # test
add_page(layout)  # test
