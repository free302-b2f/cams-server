"""패키지 초기화

 + __all__ 정의
 + 사용자 정보 DB 초기화
 + 로그인매니저 초기화"""

# region ---- __all__ 정의 ----

__all__ = ["create", "login", 'logout']

# endregion


# region ---- imports ----

import sys

import flask as fl
import flask_login as fli
import apps.utility as util
from flask_sqlalchemy import SQLAlchemy

# endregion


# region ---- DB 초기화 ----

_set = util.loadSettings("app_settings.json")["LoginManager"]
# _engine = sal.create_engine(f'postgresql://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}')
_dbUri = (
    f'postgresql://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)
_db: SQLAlchemy = None
_lm: fli.LoginManager = None

# endregion


# region ---- 모듈의 global property 정의 ----

mpb = util.ModulePropertyBuilder(sys.modules[__name__])
mpb.addProp("db", lambda: _db)
mpb.addProp("loginManager", lambda: _lm)

# endregion


# region ---- LoginManager 초기화 ----


def get_manager(server: fl.Flask) -> fli.LoginManager:
    """server 설정 및 로그인메니저 생성"""

    server.config.update(
        SECRET_KEY=_set["SECRET_KEY"],
        SQLALCHEMY_DATABASE_URI=_dbUri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    global _db, _lm
    _lm = fli.LoginManager()
    _lm.init_app(server)
    _lm.login_view = "lm.login"

    #! lm.user 모듈을 실행하기 전에 _db 초기화 필요
    _db = SQLAlchemy(server)

    #! import all Model class before create_all()
    from lm.user import User

    # create all model tables
    if _set["DropTables"]:
        _db.drop_all()
    _db.create_all()

    # --- 로그인메니저 설정 ---
    @_lm.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return _lm


# endregion
