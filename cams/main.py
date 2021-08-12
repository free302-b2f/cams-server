"""
애플리케이션의 진입점
메인 레이아웃을 표시하고 그에 대한 콜백 수행
 - display_page(): 메인 콜백함수
"""

#region ---- imports ----

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, router, error, debug, info
from apps import *

import main_layout # app's main layout
import apps.home

#endregion


app.layout = main_layout.layout

# "complete" layout
app.validation_layout = html.Div([
    app.layout,
    *router.values(),
])

@app.callback(Output('app-content', 'children'),
              Input('app-url', 'pathname'))
def display_page(pathname):
    '''주어진 경로에 해당하는 레이아웃을 리턴한다.'''

    v = router.get(pathname, apps.home.layout)
    if(callable(v)): v = v()
    return v

