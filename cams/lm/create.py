"""사용자 추가 뷰 및 콜백"""

from dash_html_components.Br import Br
from lm.imports import *
from lm.user import User


layout = html.Div(
    [
        html.H1("Create User Account"),
        dcc.Location(id="lm-create-url", refresh=True),
        dcc.Input(
            id="lm-create-username",
            type="text",
            placeholder="login name",
            maxLength=User.max_username,
            required=True,
        ),
        html.Br(),
        dcc.Input(
            id="lm-create-password",
            type="password",
            placeholder="password",
            maxLength=User.max_password,
            required=True,
        ),
        html.Br(),
        dcc.Input(
            id="lm-create-password-confirm",
            type="password",
            placeholder="password",
            maxLength=User.max_password,
            required=True,
        ),
        html.Br(),
        dcc.Input(
            id="lm-create-email",
            type="email",
            placeholder="email",
            maxLength=User.max_email,
            required=True,
        ),
        html.Br(),
        html.Button(
            "Create User",
            id="lm-create-submit",
            n_clicks=0,
        ),
        html.Div(id="lm-create-status", className="text-danger"),
        html.Div(
            [
                html.Br(),
                "Already have a user account? ",
                dcc.Link("Login!", href="lm.login"),
            ],
            className="text-info",
        ),
    ]
)


def status_error(n_clicks):
    return [html.H3(f"Sing up failed({n_clicks}). Please try again.")]


def status_success(username: str):
    return [
        html.H3(f'Account "{username}" registered.'),
        dcc.Link("Click here to Log In", href="lm.login"),
    ]


from app import app, add_page


@app.callback(
    Output("lm-create-status", "children"),
    Input("lm-create-submit", "n_clicks"),
    State("lm-create-username", "value"),
    State("lm-create-password", "value"),
    State("lm-create-password-confirm", "value"),
    State("lm-create-email", "value"),
)
def insert_users(n_clicks, un, pw, pwc, em):
    """새 사용자를 추가한다"""

    if n_clicks > 0:
        if un is None or pw is None or em is None or (pw != pwc):
            return status_error(n_clicks)

        user = User(
            username=un,
            email=em,
            password=wsec.generate_password_hash(pw, method="sha256"),
        )
        db.session.add(user)
        db.session.commit()

        return status_success(un)
    return ""


# 이 페이지를 메인 라우터에 등록한다.
add_page(layout, "Sign Up")  # test
# add_page(layout) #test
