"""패키지 초기화
+ __all__ 정의
+ 로그인매니저 초기화
"""

# region ---- __all__ 정의 ----

__all__ = ["signup", "login", "logout", "profile"]

# endregion


# region ---- imports ----

from app import debug
import sys

import flask as fl
import flask_login as fli
import apps.utility as util

# endregion

_set = util.loadSettings("app_settings.json")["LoginManager"]
_lm: fli.LoginManager = None


# region ---- 모듈의 global property 정의 ----

mpb = util.ModulePropertyBuilder(sys.modules[__name__])
mpb.addProp("loginManager", lambda: _lm)
mpb.addProp("login_view", lambda: _lm.login_view)
mpb.addProp("signup_view", lambda: _lm.signup_view)
mpb.addProp("profile_view", lambda: _lm.profile_view)

# endregion


# region ---- LoginManager 초기화 ----

# TODO: load from config file
_PUBLIC_PATH = ["/static", "/_dash", "/assets", "/favicon.ico"]


def init_app(
    server: fl.Flask, loginView: str, signupView: str, profileView: str
) -> fli.LoginManager:
    """server 설정 및 로그인메니저 생성"""

    server.config.update(
        SECRET_KEY=_set["SECRET_KEY"],
    )

    global _lm
    _lm = fli.LoginManager()
    _lm.init_app(server)
    _lm.login_view = loginView
    _lm.signup_view = signupView
    _lm.profile_view = profileView

    # region ----[ request middle ware ]----
    # @server.before_request
    def authentication_logic():
        """
        + 모든 요청에 대한 인증요구사항을 처리한다
        + '/static', login view, singup view는 통과
        + 뷰함수의 'is_public' 속성이 True이면 통과
        *** dash app에서는 작동하지 않음! ***
        """

        for x in _PUBLIC_PATH:
            if fl.request.path.startswith(x):
                return
        if fl.request.path.startswith(_lm.login_view):
            return
        if fl.request.path.startswith(_lm.signup_view):
            return
        if getattr(server.view_functions[fl.request.endpoint], "is_public", False):
            return

        if fli.current_user and fli.current_user.is_authenticated:
            return

        return fl.render_template("login.html")  # , next=fl.request.endpoint)

    # endregion

    # --- 로그인메니저 user_loader 설정 ---
    from db import loadUser

    @_lm.user_loader
    def load_user(user_id):
        return loadUser(user_id)

    return _lm


# endregion


# decorator: no needs login
def public_endpoint(function):
    function.is_public = True
    return function
