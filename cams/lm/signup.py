"""사용자 추가 뷰 및 콜백"""

from dash_html_components.Br import Br
from lm.imports import *
import db.user as db  # import User, insertUser

from lm.signup_view import layout

def status_error(n_clicks):
    return [html.H3(f"Sing up failed({n_clicks}). Please try again.")]


def status_success(username: str):
    return [
        html.H3(f'Account "{username}" registered.'),
        dcc.Link("Click here to Log In", href="lm-login"),
    ]


from app import app, add_page


@app.callback(
    Output("lm-signup-status", "children"),
    Input("lm-signup-submit", "n_clicks"),
    State("lm-signup-username", "value"),
    State("lm-signup-password", "value"),
    State("lm-signup-password-confirm", "value"),
    State("lm-signup-email", "value"),
)
def insert_user(n_clicks: int, un: str, pw: str, pwc: str, em: str):
    """새 사용자를 추가한다"""

    if n_clicks > 0:

        if un is None or pw is None or em is None or (pw != pwc):
            return status_error(n_clicks)

        un = un.strip()
        pw = pw.strip()
        pwc = pwc.strip()
        em = em.strip()
        if pw != pwc:
            return status_error(n_clicks)

        user = db.firstBy(filterBy={"username": un})
        if user:
            return status_error(n_clicks)
        else:
            db.insert(username=un, password=pw, email=em)
            return status_success(un)
    return ""


# 이 페이지를 메인 라우터에 등록한다.
# add_page(layout, "Sign Up")  # test
add_page(layout, "SIGNUP")  # test
