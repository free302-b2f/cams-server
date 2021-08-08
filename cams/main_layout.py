"""
애플리케이션의 메인 레이아웃
 - 컨테이너(div)  : app-container
 - 메뉴바(Navbar) : app-sidebar
 - 페이지 컨텐츠   : app-content
 - Location 제어기: url
"""

#region ---- imports ----
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, sidebar_items as sb
#endregion

# company logo & link to web site 
brand = dbc.NavLink([
        html.Img(src='/assets/logo_1140x742.png'),
        #'Bit2Farm',
    ], href="https://www.bit2farm.com", target='brand-window', id='sidebar-brand')

#app.sidebar_items에 등록된 메뉴항목에 대한 NavLink 생성
pages = [dbc.NavLink(sb[k][0], href=sb[k][1], active="partial") for k in sorted(sb)]

#login status & link
pages.append(
    html.Div(dbc.NavLink('UserName', href="logout"), id='sidebar-login'))

#----[임시항목: GitHub Repository ]----
pages.append(
    html.Div(dbc.NavLink('GitHub', 
        href="https://github.com/free302-b2f/cams-server", target="github"), 
    id='sidebar-github'))

#메인 레이아웃 - 메뉴바 
sidebar = dbc.Navbar(
    [   
        brand,
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(dbc.Nav(pages, pills=True), id="navbar-collapse", navbar=True, is_open=False),
    ],
    color='dark',#'dark',#'light', #"primary",
    dark=True,
    sticky='top',
    className='app-sidebar',
)

#메인 레이아웃 - 페이지 내용
content = html.Div(id="app-content", className="app-content")

#메인 레이아웃 - 주소표시줄 제어
locator = dcc.Location(id='url', refresh=False)

#메인 레이아웃
layout = html.Div([locator, sidebar, content], className="app-container")

# callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open): 
    return not is_open if n else is_open

