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
        html.Div(children="", id="lm-logout-status", className="text-danger"),
    ]
)


def status_success(username: str):
    return [
        html.H3(f"User '{username}' logged out."),
        dcc.Link("Home", href="apps.home"),
    ]


def status_error(n_clicks):
    return [
        html.H3(f"Log out failed({n_clicks}). Please try again."),
        dcc.Link("LogIn", href="lm.login"),
    ]


@app.callback(
    Output("lm-logout-status", "children"),
    Output("lm-logout-status", "className"),
    Output("lm-logout-url", "pathname"),
    Input("lm-logout-ok", "n_clicks"),
    Input("lm-logout-cancel", "n_clicks"),
)
def logout_handler(n_ok: int, n_cancel: int):
    """Logout Callback"""

    if (n_ok > 0) and util.callback_triggered_by(["lm-logout-ok"]):
        if (
            hasattr(fli.current_user, "is_authenticated")
            and fli.current_user.is_authenticated
        ):
            username = fli.current_user.username
            fli.logout_user()
            return status_success(username), "text-info", "apps.home"  # TODO: go home?
        else:
            return status_error(n_ok), "text-danger", dash.no_update

    if (n_cancel > 0) and util.callback_triggered_by(["lm-logout-cancel"]):
        return "Logout canceled", "text-info", dash.no_update  # TODO: go previous page

    return "", "", dash.no_update


# 이 페이지를 메인 라우터에 등록한다.
# add_page(layout, "Log Out")  # test
add_page(layout) #test
