# -*- coding: utf-8 -*-

#region ---- imports ----

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#from apps import *
from app import app
import app_layout # app's main layout

#endregion

app.layout = app_layout.layout

# "complete" layout
app.validation_layout = html.Div([
    app.layout,
])

@app.callback(Output('app-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    return 'no page selected'

