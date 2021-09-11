"""메인 메뉴바에 로그인 상태를 출력하는 모듈

+ app-url의 pathname 변경시마다 로그인 상태가 반영된 링크를 생성한다.
+ 링크 주소에 따라 페이지 갱신여부 결정하며 갱신시 flask page로 이동한다.
"""

from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app, add_page, debug

import lm
from dash import no_update


layout = html.Div(id="app-sidebar-login")


@app.callback(
    Output("app-sidebar-login", "children"),
    Output("lm-storage", "data"),
    Input("app-url", "pathname"),
)
def login_status(appPath):
    """메인 메뉴바에 로그인 상태를 표시하는 콜백"""

    username, userId = "Login", "0"
    pathname, refresh = lm.login_view, True
    icon, iconClass = "account_circle", "material-icons-two-tone md-light"

    if fli.current_user.is_authenticated:
        username, userId = fli.current_user.username, fli.current_user.get_id()
        pathname, refresh = lm.profile_view, False
        icon, iconClass = "manage_accounts", "material-icons-two-tone md-light"

    # <span class="material-icons-two-tone">account_circle</span>
    link = dbc.NavLink(
        [
            html.Span(icon, className=iconClass),
            username,
        ],
        href=pathname,
        external_link=refresh,
    )
    debug(login_status, f"{appPath= }, {refresh= }")

    return link, userId
