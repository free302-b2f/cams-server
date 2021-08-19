"""사용자 확인을 받아 WSGI 앱 재시작하는 레이아웃과 콜백"""

from apps.imports import *
import os
from dash import no_update


# 팝업 레이아웃
modal = util.buildPopup(
    id="app-sidebar-restart-modal",
    header="Restarting CAMs",
    body=[
        html.H4(
            "Going to restart CAMs... Are you sure?",
            id="app-sidebar-restart-status",
            className="text-info",
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
        dcc.Location("app-sidebar-restart-url", refresh=True),
    ],
)


@app.callback(
    Output("app-sidebar-restart-modal", "is_open"),
    Output("app-sidebar-restart-status", "children"),
    Output("app-sidebar-restart-status", "className"),
    Output("app-sidebar-restart-ok", "disabled"),
    Output("app-sidebar-restart-cancel", "disabled"),
    Input("app-sidebar-restart", "n_clicks"),
    Input("app-sidebar-restart-ok", "n_clicks"),
    Input("app-sidebar-restart-cancel", "n_clicks"),
)
def show_modal(n_show, n_ok, n_cancel):
    """팝업을 띄우고 사용자 입력에 대한 반응을 처리하는 콜백"""

    nop = (False, no_update, no_update, no_update, no_update)

    if n_show == 0 and n_ok == 0 and n_cancel == 0:
        return nop

    if util.callback_triggered_by(["app-sidebar-restart"]):
        return True, no_update, no_update, no_update, no_update

    if util.callback_triggered_by(["app-sidebar-restart-ok"]):
        return True, "Restarting...", "text-danger", True, True

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
