"""애플리케이션의 진입점

 + 모든 페이지를 임포트하고 메뉴바에 등록한다.
 + 모든 페이지의 레이아웃을 검증한다.
 + 메인 레이아웃을 표시하고 그에 대한 콜백 수행한다.
   - display_page(): 메인 콜백함수
"""

from dash.dependencies import Input, Output, State
from dash import no_update
# import flask as fl
import flask_login as fli
from utility import error, debug, info, loadAppSettings

# apply style from app_settings
with open("assets/css/html.css", "w") as fp:
    size = loadAppSettings("Cams")["CSS_FONT_SIZE_%"]
    fp.write(f"html{{ font-size: {size}%; }}")

# init app
from app import app, router, getSettings
with app.server.app_context():

    # db, lm 패키지 초기화 & 하위모듈 로딩
    import db
    from db.user import AppUser

    settings = getSettings("Cams")
    if settings["DB_DO_RESET"]:
        db.drop_create_seed()
    import lm

    #! main_layout을 임포트 하기전 메뉴등록하는 모듈 전부 임포트
    from apps import *
    from admin import *
    import main_layout

    # "complete" layout
    app.validation_layout = [app.layout, *router.values()]


# region ----[ NavBar Toggler Callback ]----


@app.callback(
    Output("app-sidebar-collapse", "is_open"),
    Input("app-sidebar-toggler", "n_clicks"),
    State("app-sidebar-collapse", "is_open"),
)
def toggle_navbar_collapse(n, is_open):
    """callback for toggling the collapse on small screens"""

    return not is_open if n else is_open


# endregion


# region ----[ Main Callback ]----


@app.callback(
    Output("app-content", "children"),
    Output("app-url-refresh", "pathname"),
    Input("app-url", "pathname"),
)
def display_page(appPath: str):
    """주어진 경로에 해당하는 레이아웃을 리턴한다."""

    debug(display_page, f"{appPath = }")

    # 사용자 인증 상태 체크
    user: AppUser = fli.current_user
    if user == None or not user.is_authenticated:
        debug(display_page, f"redirecting: {appPath} -> {lm.login_view()}")
        return no_update, lm.login_view()

    # 경로의 레이아웃 얻기
    v = router.get(appPath, None)

    # 레이아웃이 없는 경우 프로필/대시보드로 이동
    if v is None:
        error(f"Layout of {appPath=} is 'None'")
        return no_update, lm.profile_view()

    # 함수형 레아아웃에 대하여 함수 출력 얻기
    if callable(v):
        v = v()

    return v, no_update


# endregion


# region ----[ start websocket server ]----

# import os

# dir = os.path.join(app.server.root_path, "static", "ircam")
# startWsServer(dir)

# endregon
