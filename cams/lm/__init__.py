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

login_view = lambda: _lm.login_view
signup_view = lambda: _lm.signup_view
profile_view = lambda: _lm.profile_view

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

    # --- 로그인메니저 user_loader 설정 ---
    from db.user import AppUser

    @_lm.user_loader
    def load_user(user_id):
        return AppUser.query.get(user_id)

    return _lm


# endregion
