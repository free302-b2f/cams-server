"""애플리케이션의 진입점

 + 모든 페이지를 임포트하고 메뉴바에 등록한다.
 + 모든 페이제의 레이아웃을 검증한다.
 + 메인 레이아웃을 표시하고 그에 대한 콜백 수행한다.
   - display_page(): 메인 콜백함수
"""

# region ---- imports ----

from dash.dependencies import Input, Output

from app import app, router, error, debug, info
from apps import *

import main_layout  # app's main layout
import apps.home

# endregion

#메인 레이아웃
app.layout = main_layout.layout

# "complete" layout
app.validation_layout = [ app.layout, *router.values()]


@app.callback(Output('app-content', 'children'),
              Input('app-url', 'pathname'))
def display_page(pathname):
    '''주어진 경로에 해당하는 레이아웃을 리턴한다.'''

    debug(f'{pathname = }')
    v = router.get(pathname, apps.home.layout)
    if(callable(v)):
        v = v()
    return v
