"""로그인 뷰 및 콜백"""

from dash_html_components.Br import Br
from dash_html_components.Span import Span
from lm.imports import *
from lm.user import User

layout = html.Div(
    [
        dcc.Location(id="lm-login-url", refresh=True),
        html.H3("""Please log in to continue:""", id="h1"),
        dcc.Input(
            placeholder="login name",
            type="text",
            id="lm-login-uname-box",
            required=True,
        ),
        html.Br(),
        dcc.Input(
            placeholder="password",
            type="password",
            id="lm-login-pwd-box",
            required=True,
        ),
        html.Br(),
        html.Button(
            children="Login", n_clicks=0, type="submit", id="lm-login-login-button"
        ),
        html.Br(),
        html.Div(children="", id="lm-login-status", className="text-danger"),
        html.Div(
            [
                html.Br(),
                "Have no account? ",
                dcc.Link("Sign Up!", href="lm.create"),
            ],
            className="text-info",
        ),
    ]
)


def status_success(username: str):
    return [html.H3("Login successful."), dcc.Link("Home", href="/")]


def status_error(n_clicks):
    return [html.H3(f"Log in Failed({n_clicks}). Please try again.")]


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
        user = User.query.filter_by(username=input1).first()
        if user:
            if wsec.check_password_hash(user.password, input2):
                fli.login_user(user)
                return dash.no_update, status_success(user.username)

        return dash.no_update, status_error(n_clicks)
    return dash.no_update, ""


# 이 페이지를 메인 라우터에 등록한다.
add_page(layout, "Login") #test
#add_page(layout) #test