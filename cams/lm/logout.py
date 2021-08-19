"""로그아웃 뷰 및 콜백"""

from dash_html_components.Div import Div
from sqlalchemy.sql.expression import false
from lm.imports import *
from db.user import User
from app import app, add_page
from dash import no_update

_status = html.H4(
    "Going to log out.  Are you sure?",
    className="text-info",
)

_modal = util.buildPopup(
    id="lm-logout-modal",
    header="Logging Out",
    body=[
        html.Div(_status, id="lm-logout-status"),
        html.Div(id="lm-logout-dummy"),
        dcc.Location("lm-logout-url", refresh=True),
    ],
    footer=[
        dbc.Button(
            " OK ",
            color="primary",
            id="lm-logout-ok",
            n_clicks=0,
            disabled=False,
        ),
        dbc.Button(
            "Cancel",
            color="secondary",
            id="lm-logout-cancel",
            n_clicks=0,
            disabled=False,
        ),
    ],
)

layout = html.Div(
    [
        dbc.Button("LogOut", n_clicks=0, id="lm-logout-button", color="primary"),
        _modal,
    ]
)


def status_success(username: str):
    return html.H3(f"User '{username}' logged out.", className="text-info")


def status_error(n_clicks):
    return html.H3(
        f"Log out failed({n_clicks}). Please try again.", className="text-danger"
    )


@app.callback(
    Output("lm-logout-modal", "is_open"),
    Output("lm-logout-status", "children"),
    Output("lm-logout-url", "pathname"),
    Input("lm-logout-button", "n_clicks"),
    Input("lm-logout-ok", "n_clicks"),
    Input("lm-logout-cancel", "n_clicks"),
)
def logout_handler(n_show: int, n_ok: int, n_cancel: int):
    """Logout Callback"""

    nop = (False, no_update, no_update)

    if not (n_show or n_ok or n_cancel):
        return nop

    if util.callback_triggered_by(["lm-logout-button"]):
        return True, no_update, no_update

    if util.callback_triggered_by(["lm-logout-ok"]):
        if fli.current_user.is_authenticated:
            username = fli.current_user.username
            fli.logout_user()
            return no_update, status_success(username), "apps.home"
        else:
            return no_update, status_error(n_ok), dash.no_update

    return nop
    