# -*- coding: utf-8 -*-

#region ---- imports ----
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app
#endregion

apps = ['no-app']
navs = dbc.Nav(apps, pills=True)

sidebar = dbc.Navbar(
    [        
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(navs, id="navbar-collapse", navbar=True, is_open=False),
    ],
    color='dark',#'dark',#'light', #"primary",
    dark=True,
    className='app-sidebar',
)

content = html.Div(id="app-content", className="app-content")
locator = dcc.Location(id='url', refresh=False)

layout = html.Div([locator, sidebar, content], className="app-container")

# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open): 
    return not is_open if n else is_open

