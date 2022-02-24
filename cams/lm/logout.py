"""로그아웃 뷰 및 콜백"""

print(f"<{__name__}> loading...")

from lm._imports import *
from db.user import AppUser
from app import app, addPage
from dash import no_update

_body_msg = html.H4(
    "Going to log out.  Are you sure?", className="text-info", id="lm-logout-status"
)

_header = dbc.ModalHeader("Logging Out", className="font-small-caps")
_body = dbc.ModalBody(
    [
        _body_msg,  # html.Div(_body_msg, id="lm-logout-status"),
        # html.Div(id="lm-logout-dummy"),
        dcc.Location("lm-logout-url", refresh=True),
    ]
)

# <span class="material-icons-two-tone">check_circle</span>
_footer_ok = [
    html.Span("done", className="material-icons-two-tone"),
    html.Span("OK"),
]
_footer = dbc.ModalFooter(
    [
        dbc.Button(
            _footer_ok,  # " OK ",
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
    ]
)

# 로그아웃 링크/버튼 - 다른 페이지에서 사용
# <span class="material-icons-two-tone">logout</span>
_logout_button = [
    html.Span("Logout"),
    html.Span("logout", className="material-icons-two-tone"),
]
layout = [
    # dbc.Button(_layout_button, n_clicks=0, id="lm-logout-button", color="primary"),
    html.A(
        _logout_button,
        n_clicks=0,
        id="lm-logout-button",
        href="javascript:void()",
        className="flex-h mr1",
    ),
    # dcc.Link(_logout_button, id="lm-logout-button", href=""),
    dbc.Modal([_header, _body, _footer], id="lm-logout-modal"),
]


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
