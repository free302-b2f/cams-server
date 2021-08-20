"""메인 메뉴바에 로그인 상태를 출력하는 모듈"""

from dash_html_components.Span import Span
from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app, add_page

layout = html.Div(id="app-sidebar-login")


@app.callback(
    Output("app-sidebar-login", "children"),
    Output("lm-storage", "data"),
    Input("app-url", "pathname"),
)
def login_status(url):
    """메인 메뉴바에 로그인 상태를 표시하는 콜백"""

    username, userId = "Login", "0"
    pathname, iconClass, icon = "lm.login", "material-icons-two-tone md-light", "account_circle"

    if fli.current_user.is_authenticated:
        username, userId = fli.current_user.username, fli.current_user.get_id()
        pathname  = "lm.profile"
        iconClass, icon = "material-icons-two-tone md-light", "manage_accounts"

    # TODO: NavLink 대신 popup 사용?
    # <span class="material-icons-two-tone">account_circle</span>
    link = [
        html.Span(icon, className=iconClass),
        username,
    ]
    nav = (dbc.NavLink(link, href=pathname), userId)

    return nav
