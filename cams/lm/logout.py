"""로그아웃 뷰 및 콜백"""

from lm.imports import *
from db.user import User
from app import app, add_page

layout = html.Div(
    [
        dcc.Location(id="lm-logout-url", refresh=True),
        html.H3("Logging Out?"),
        html.Br(),
        #! if not set 'n_clicks' it is None
        dbc.Button("OK", id="lm-logout-ok", color="primary", n_clicks=0),
        dbc.Button("Cancel", id="lm-logout-cancel", color="secondary", n_clicks=0),
        html.Br(),
        html.Div(children="", id="lm-logout-status"),
    ]
)


def status_success(username: str):
    return [
        html.H3(f"User '{username}' logged out.", className="text-info"),
        dcc.Link("Home", href="apps.home"),
    ]


def status_error(n_clicks):
    return [
        html.H3(f"Log out failed({n_clicks}). Please try again.", className="text-danger"),
        dcc.Link("LogIn", href="lm.login"),
    ]

def status_cancel(n_clicks):
    return [
        html.H3(f"Logout canceled({n_clicks}).", className="text-info"),
    ]


@app.callback(
    Output("lm-logout-status", "children"),
    Output("lm-logout-url", "pathname"),
    Input("lm-logout-ok", "n_clicks"),
    Input("lm-logout-cancel", "n_clicks"),
)
def logout_handler(n_ok: int, n_cancel: int):
    """Logout Callback"""

    if n_ok == 0 and n_cancel == 0:
        return "", dash.no_update

    if util.callback_triggered_by(["lm-logout-ok"]):
        if fli.current_user.is_authenticated:
            username = fli.current_user.username
            fli.logout_user()
            return status_success(username), "apps.home"  # TODO: go home?
        else:
            return status_error(n_ok), dash.no_update

    if util.callback_triggered_by(["lm-logout-cancel"]):
        return status_cancel(n_cancel), dash.no_update  # TODO: go previous page

    return "", dash.no_update


# 이 페이지를 메인 라우터에 등록한다.
# add_page(layout, "Log Out")  # test
add_page(layout) #test
