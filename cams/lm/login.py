"""로그인 뷰 및 콜백"""

from lm.imports import *
import db.user as db  # import User, getUserByName

from lm.login_view import layout


def status_success(username: str):
    return [
        html.H3(f"User '{username}' logged in.", className="text-info"),
        dcc.Link("Home", href="apps.home"),
    ]


def status_error(n_clicks):
    return [
        html.H3(
            f"Log in failed({n_clicks}). Please try again.", className="text-danger"
        )
    ]


from app import app, add_page


@app.callback(
    Output("lm-login-url", "pathname"),
    Output("lm-login-status", "children"),
    Input("lm-login-login-button", "n_clicks"),
    State("lm-login-uname-box", "value"),
    State("lm-login-pwd-box", "value"),
)
def login_button_click(n_clicks, input1, input2):
    """로그인 뷰의 콜백"""

    if n_clicks > 0:
        user = db.firstBy(filterBy={"username": input1})
        if user:
            if wsec.check_password_hash(user.password, input2):
                fli.login_user(user)
                return "apps.home", status_success(user.username)

        return dash.no_update, status_error(n_clicks)
    return dash.no_update, ""


# 이 페이지를 메인 라우터에 등록한다.
# add_page(layout, "Log In")  # test
add_page(layout)  # test
