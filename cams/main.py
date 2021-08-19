"""애플리케이션의 진입점

 + 모든 페이지를 임포트하고 메뉴바에 등록한다.
 + 모든 페이지의 레이아웃을 검증한다.
 + 메인 레이아웃을 표시하고 그에 대한 콜백 수행한다.
   - display_page(): 메인 콜백함수
"""

# region ---- imports ----

import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import flask_login as fli

from app import app, router, debug
from db import *
from lm import *
from apps import *

#! main_layout을 임포트 하기전에 다른 페이지를 전부 임포트해야한다.
import apps.home
import main_layout

# endregion


# "complete" layout
app.validation_layout = [app.layout, *router.values()]


@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar_collapse(n, is_open):
    """callback for toggling the collapse on small screens"""

    return not is_open if n else is_open


@app.callback(Output("app-content", "children"), Input("app-url", "pathname"))
def display_page(pathname):
    """주어진 경로에 해당하는 레이아웃을 리턴한다."""

    debug(f"{pathname = }")
    v = router.get(pathname, apps.home.layout)
    if callable(v):
        v = v()
    return v


@app.callback(
    Output("sidebar-login", "children"),
    Output("app-storage", "data"),
    Input("app-url", "pathname"),
)
def login_status(url):
    """callback to display login/logout link in the header"""

    status, pathname, userId = 'Login', 'lm.login', 'anonymous'
    if fli.current_user.is_authenticated: 
        status, pathname = fli.current_user.username, 'lm.logout'
        userId = fli.current_user.get_id()

    return dbc.NavLink(status, href=pathname), userId

    
application = app.server