"""패키지 초기화
+ __all__ 정의
+ 로그인매니저 초기화
"""

# region ---- __all__ 정의 ----

__all__ = ["create", "login", "logout"]

# endregion


# region ---- imports ----

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

# endregion


# region ---- LoginManager 초기화 ----


def init_app(server: fl.Flask) -> fli.LoginManager:
    """server 설정 및 로그인메니저 생성"""

    server.config.update(
        SECRET_KEY=_set["SECRET_KEY"],
    )

    global _lm
    _lm = fli.LoginManager()
    _lm.init_app(server)
    _lm.login_view = "lm.login"

    from db import loadUser

    # --- 로그인메니저 설정 ---
    @_lm.user_loader
    def load_user(user_id):
        return loadUser(user_id)

    return _lm


# endregion
