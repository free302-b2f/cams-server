"""메인 메뉴바에 로그인 상태를 출력하는 모듈"""

from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app, add_page

layout = html.Div(
    [
        dcc.Store(id="lm-storage", storage_type="session"),
        html.Div(id="app-sidebar-login-link"),
    ],
    id="app-sidebar-login",
)


@app.callback(
    Output("app-sidebar-login-link", "children"),
    Output("lm-storage", "data"),
    Input("app-url", "pathname"),
)
def login_status(url):
    """메인 메뉴바에 로그인 상태를 표시하는 콜백"""

    status, pathname, userId = "Login", "lm.login", "anonymous"

    if fli.current_user.is_authenticated:
        status, pathname = fli.current_user.username, "lm.profile"
        userId = fli.current_user.get_id()

    # TODO: NavLink 대신 popup 사용?
    link = (dbc.NavLink(status, href=pathname), userId)

    return link
