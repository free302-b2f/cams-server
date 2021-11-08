"""
애플리케이션의 메인 레이아웃
 - 컨테이너(div)  : app-container
 - 메뉴바(Navbar) : app-sidebar
 - 페이지 컨텐츠   : app-content
 - Location 제어기: app-url
"""

print(f"<{__name__}> loading...")

# region ---- imports ----

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

from app import app, sidebar_items as sb

# endregion


# NavBar Brand : company logo & website link
brand = dbc.NavLink(
    html.Img(src="/assets/img/logo_1140x742.png"),
    href="https://www.bit2farm.com",
    target="brand-window",
    id="app-sidebar-brand",
)

# app.sidebar_items에 등록된 메뉴항목에 대한 NavLink 생성
pages = [
    dbc.NavLink(
        sb[key][0],  # menu title
        href=sb[key][1],  # path
        active="partial",
        n_clicks=0,
        id=f"app-sidebar-{sb[key][2]}",  # element id
    )
    for key in sorted(sb)
]


# login status & user profile
import lm.status

pages.append(lm.status.layout)


# ----[임시항목: GitHub Repository ]----
pages.append(
    dbc.NavLink(
        html.Div(),
        href="https://github.com/free302-b2f/cams-server",
        target="github",
        n_clicks=0,
        id="app-sidebar-github",
    )
)


# ----[임시항목: restart CAMs ]----
import apps.restart

pages.append(apps.restart.layout)


# 메인 레이아웃 - 메뉴바
sidebar = dbc.Navbar(
    [
        brand,
        dbc.NavbarToggler(id="app-sidebar-toggler", n_clicks=0),
        dbc.Collapse(
            dbc.Nav(pages, pills=True),
            id="app-sidebar-collapse",
            navbar=True,
            is_open=False,
        ),
    ],
    color="dark",  #'dark',#'light', #"primary",
    dark=False,
    sticky="top",
    id="app-sidebar",
)

# 메인 레이아웃 - 페이지 내용
content = html.Div(
    id="app-content",
    className="flex-v-center",
)

# 메인 레이아웃 - 주소표시줄 제어
locator = [
    dcc.Location(id="app-url", refresh=False),
    dcc.Location(id="app-url-refresh", refresh=True),
]

# 로그인 상태 스토리지
store = dcc.Store(id="lm-storage", storage_type="session")

# 메인 레이아웃 설정
app.layout = html.Div([store, *locator, sidebar, content], id="app-container")
