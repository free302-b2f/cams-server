"""로그인 뷰"""

from lm.imports import *
from lm._view_css_ import CSS_LINK
import db.user as db  # import User, getUserByName

layout = html.Div(
    [
        *CSS_LINK,
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
                                    dcc.Link("Sign Up!", href="lm-signup"),
                                ],
                                className="d-flex justify-content-center links",
                            ),
                            html.Div(
                                dcc.Link("Forgot your password?", href="#"),
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
