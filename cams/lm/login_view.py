"""로그인 뷰"""

from lm.imports import *
import db.user as db  # import User, getUserByName

layout = html.Div(
    [
        html.Link(
            rel="stylesheet",
            href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
            integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO",
            crossOrigin="anonymous",
        ),
        html.Link(
            rel="stylesheet",
            href="https://use.fontawesome.com/releases/v5.3.1/css/all.css",
            integrity="sha384-mzrmE5qonljUremFsqc01SB46JvROS7bZs3IO2EmfFsd15uHvIt+Y8vEf7N7fWAU",
            crossOrigin="anonymous",
        ),
        # html.Link(
        #     rel="stylesheet",
        #     href="/assets/login.css",
        # ),
        dcc.Location(id="lm-login-url", refresh=True),
        html.Div(
            html.Div(
                [
                    # card-header
                    html.Div(
                        [
                            html.H3("Sign In", className="font-small-caps"),
                            html.Div(
                                [
                                    html.Span(
                                        html.I(className="fab fa-facebook-square")
                                    ),
                                    html.Span(
                                        html.I(className="fab fa-google-plus-square")
                                    ),
                                    html.Div(id="lm-login-kakao"),
                                ],
                                className="d-flex justify-content-end social_icon",
                            ),
                        ],
                        className="card-header",
                    ),
                    # card-body
                    html.Div(
                        [
                            # username
                            html.Div(
                                [
                                    html.Div(
                                        html.Span(
                                            html.I(className="fas fa-user"),
                                            className="input-group-text",
                                        ),
                                        className="input-group-prepend",
                                    ),
                                    dcc.Input(
                                        id="lm-login-uname-box",
                                        maxLength=db.User.max_username,
                                        type="text",
                                        className="form-control",
                                        placeholder="login id",
                                        required=True,
                                    ),
                                ],
                                className="input-group form-group",
                            ),
                            # password
                            html.Div(
                                [
                                    html.Div(
                                        html.Span(
                                            html.I(className="fas fa-key"),
                                            className="input-group-text",
                                        ),
                                        className="input-group-prepend",
                                    ),
                                    dcc.Input(
                                        id="lm-login-pwd-box",
                                        type="password",
                                        className="form-control",
                                        placeholder="password",
                                        maxLength=db.User.max_password,
                                        required=True,
                                    ),
                                ],
                                className="input-group form-group",
                            ),
                            # remember me
                            dcc.Checklist(
                                options=[{"label": "Remember Me", "value": 1}],
                                className="row align-items-center remember",
                            ),
                            # submit
                            html.Div(
                                dbc.Button(
                                    id="lm-login-login-button",
                                    children="Login",
                                    n_clicks=0,
                                    type="submit",
                                    className="btn float-right login_btn",
                                ),
                                className="form-group",
                            ),
                        ],
                        className="card-body",
                    ),
                    # card-footer
                    html.Div(
                        [
                            html.Div(
                                [
                                    "Don't have an account?",
                                    dcc.Link("Sign Up!", href="lm-create"),
                                ],
                                className="d-flex justify-content-center links",
                            ),
                            html.Div(
                                dcc.Link("Forgot your password?", href="lm-create"),
                                className="d-flex justify-content-center",
                            ),
                        ],
                        className="card-footer",
                    ),
                ],
                className="card",
            ),
            className="d-flex justify-content-center h-100",
        ),
        html.Div(id="lm-login-status"),
    ],
    id="app-loginpage",
)
