"""사용자 확인을 받아 WSGI 앱 재시작하는 레이아웃과 콜백"""

print(f"<{__name__}> loading...")

from ._imports import *
import os
from dash import no_update
import dash_bootstrap_components as dbc
from utility import buildPopup, callback_triggered_by

# 팝업 레이아웃
_status = html.H4(
    "Going to restart CAMs. Are you sure?",
    className="text-info",
)
_statusOk = html.H4(
    "Restarting...",
    className="text-danger",
)
_modal = buildPopup(
    id="app-sidebar-restart-modal",
    header="Restarting CAMs",
    body=[
        html.Div(
            _status,
            id="app-sidebar-restart-status",
        ),
        html.Div(id="app-sidebar-restart-dummy"),
    ],
    footer=[
        dbc.Button(
            " OK ",
            color="primary",
            id="app-sidebar-restart-ok",
            n_clicks=0,
            disabled=False,
        ),
        dbc.Button(
            "Cancel",
            color="secondary",
            id="app-sidebar-restart-cancel",
            n_clicks=0,
            disabled=False,
        ),
    ],
)

# 메인메뉴 레이아웃
layout = html.Div(
    [
        dbc.Button(
            html.Span("restart_alt", className="material-icons-two-tone md-color"),
            # "RESTART",
            n_clicks=0,
            id="app-sidebar-restart",
            color="transparent"),
        _modal,
    ]
)


@app.callback(
    Output("app-sidebar-restart-modal", "is_open"),
    Output("app-sidebar-restart-status", "children"),
    Output("app-sidebar-restart-ok", "disabled"),
    Output("app-sidebar-restart-cancel", "disabled"),
    Input("app-sidebar-restart", "n_clicks"),
    Input("app-sidebar-restart-ok", "n_clicks"),
    Input("app-sidebar-restart-cancel", "n_clicks"),
)
def show_modal(n_show, n_ok, n_cancel):
    """팝업을 띄우고 사용자 입력에 대한 반응을 처리하는 콜백"""

    nop = (False, no_update, no_update, no_update)

    if not (n_show or n_ok or n_cancel):
        return nop

    if callback_triggered_by(["app-sidebar-restart"]):
        return True, no_update, no_update, no_update

    if callback_triggered_by(["app-sidebar-restart-ok"]):
        return True, _statusOk, True, True

    return nop


@app.callback(
    Output("app-sidebar-restart-dummy", "children"),
    Input("app-sidebar-restart-status", "children"),
)
def call_restart(status):
    """CAMs 재시작 트리거를 발생시키는 콜백"""

    fn = os.path.join(app.server.root_path, "wsgi.py")
    if os.name == "nt":
        os.system(f"copy /b {fn} +,,")
    else:
        os.system(f"touch {fn}")

    return no_update
