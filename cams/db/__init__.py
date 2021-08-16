"""패키지 초기화
 + __all__ 정의
 + SQLAlchemy DB 초기화
 """

# region ---- __all__ 정의 ----

__all__ = []

# endregion


# region ---- imports ----

import sys
from types import FunctionType

import flask as fl
import flask_login as fli
import apps.utility as util
from flask_sqlalchemy import SQLAlchemy

# endregion


# region ---- DB 초기화 ----

_set = util.loadSettings("app_settings.json")["Postgres"]
_dbUri = (
    f'postgresql://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)
_db: SQLAlchemy = None
_load_user: FunctionType = None

# endregion


# region ---- 모듈의 global property 정의 ----

mpb = util.ModulePropertyBuilder(sys.modules[__name__])
mpb.addProp("db", lambda: _db)
mpb.addProp("loadUser", lambda: _load_user)

# endregion


# region ---- app 초기화 ----


def init_app(server: fl.Flask) -> fli.LoginManager:
    """server 설정 및 로그인메니저 생성"""

    server.config.update(
        SQLALCHEMY_DATABASE_URI=_dbUri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    global _db, _load_user

    #! db.xxx 모듈을 실행하기 전에 _db 초기화 필요
    _db = SQLAlchemy(server)

    #! import all models
    from db.user import User

    # import other model here...

    _load_user = User.query.get

    # create all model tables
    if _set["DropTables"]:
        _db.drop_all()
    _db.create_all()


# endregion
