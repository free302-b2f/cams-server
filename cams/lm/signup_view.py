"""사인업 뷰 - 계정생성"""

from lm.imports import *
from lm._view_css_ import CSS_LINK
import db.user as db  # import User, getUserByName

layout = html.Div(
    [
        *CSS_LINK,
        dcc.Location(id="lm-signup-url", refresh=True),
        html.Div(
            # .card
            html.Div(
                [
                    # card-header
                    html.Div(
                        [
                            html.H3("Sign Up", className="font-small-caps"),
                            html.Div(
                                
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
                                        id="lm-signup-username",
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
                                        id="lm-signup-password",
                                        type="password",
                                        className="form-control",
                                        placeholder="password",
                                        maxLength=db.User.max_password,
                                        required=True,
                                    ),
                                ],
                                className="input-group form-group",
                            ),
                            # password confirm
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
                                        id="lm-signup-password-confirm",
                                        type="password",
                                        className="form-control",
                                        placeholder="password",
                                        maxLength=db.User.max_password,
                                        required=True,
                                    ),
                                ],
                                className="input-group form-group",
                            ),
                            # email
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
                                        id="lm-signup-email",
                                        type="email",
                                        className="form-control",
                                        placeholder="email address",
                                        maxLength=db.User.max_email,
                                        required=True,
                                    ),
                                ],
                                className="input-group form-group",
                            ),
                            # submit
                            html.Div(
                                dbc.Button(
                                    id="lm-signup-submit",
                                    children="Sign Up",
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
                                    "Already have an account?",
                                    dcc.Link("Log In!", href="lm-login"),
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
                className="card", id="lm-signup-card"
            ),
            className="d-flex justify-content-center h-100",
        ),
        html.Div(id="lm-signup-status"),
    ],
    id="app-loginpage", className="app-signuppage"
)
