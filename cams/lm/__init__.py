# region ---- __all__ 정의 ----

from os.path import dirname, basename, isfile, join
import glob
from typing import Any

# modules = glob.glob(join(dirname(__file__), "*.py"))
# __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
# if 'utility' in __all__: __all__.remove('utility')
__all__ = ["login", "create"]

# endregion

import sys

import flask as fl
import flask_login as fli
import apps.utility as util
import sqlalchemy as sal  # import Table, create_engine
from flask_sqlalchemy import SQLAlchemy

_set = util.loadSettings("app_settings.json")["LoginManager"]
# _engine = sal.create_engine(f'postgresql://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}')
_dbUri = (
    f'postgresql://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)
_db: SQLAlchemy = None
_lm: fli.LoginManager = None


# region ---- 모듈의 global property 정의 ----

mpb = util.ModulePropertyBuilder(sys.modules[__name__])
mpb.addProp("db", lambda: _db)
mpb.addProp("loginManager", lambda: _lm)

# endregion


# Login manager object will be used to login / logout users
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

    #! import all Model class before create_all()
    from lm.user import User

    #! after Model loading create all model tables
    _db = SQLAlchemy(server)
    if _set['DropTables'] : _db.drop_all()
    _db.create_all()

    @_lm.user_loader
    def load_user(username):
        return User.query.get(username)

    return _lm
