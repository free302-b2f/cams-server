"""패키지 초기화
 + __all__ 정의
 + SQLAlchemy DB 초기화
 """

# region ---- __all__ 정의 ----

# __all__ = [ ]

# endregion


# region ---- imports ----

from os import name
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

# module global variables
_db: SQLAlchemy = None
_load_user: FunctionType = None
# _load_farm: FunctionType = None
# _load_sensor: FunctionType = None
# _seed_meta: FunctionType = None

# endregion


# region ---- app 초기화 ----


def init_app(server: fl.Flask) -> fli.LoginManager:
    """server 설정 및 로그인메니저 생성"""

    server.config.update(
        SQLALCHEMY_DATABASE_URI=_dbUri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    global _db, _load_user, _seed_meta

    #! db.xxx 모듈을 실행하기 전에 _db 초기화 필요
    _db = SQLAlchemy(server)
    # _db.Model.metadata.reflect(bind=_db.engine, schema=_set["Db"])

    #! import all models
    from db.user import AppUser
    from db.farm import Farm
    from db.sensor import Sensor
    
    # create all model tables & seed
    if _set["DropTables"]:
        _db.drop_all()
        # _db.Model.metadata.bind = _db.engine # drop_all()시 불필요
        # Sensor.__table__.drop(checkfirst=True)
        # Farm.__table__.drop(checkfirst=True)
        # User.__table__.drop(checkfirst=True)

        _db.create_all()
        _seed_meta()

    _load_user = AppUser.query.get
    # _load_farm = Farm.query.get
    # _load_sensor = Sensor.query.get


    pass  # init_app


def _seed_meta():
    import werkzeug.security as wsec

    #! import all models
    from db.user import AppUser
    from db.farm import Farm
    from db.sensor import Sensor

    pw = wsec.generate_password_hash("3569", method="sha256")
    
    f1 = Farm(name="KIST Pheno Lab1")
    f2 = Farm(name="KIST Pheno Lab2")
    f1.sensors.append(Sensor(sn="B2F_CAMs_1000000000001"))
    f1.sensors.append(Sensor(sn="B2F_CAMs_1000000000002"))
    f2.sensors.append(Sensor(sn="B2F_CAMs_1000000000003"))
    u = AppUser(
        username="drbae",
        password=pw,
        email="amadeus.bae@gmail.com",
        realname="Samyong Bae",
    )    
    u.farms.append(f1)
    u.farms.append(f2)
    _db.session.add(u)
    _db.session.commit()


# endregion


# region ---- 모듈의 global property 정의 ----

mpb = util.ModulePropertyBuilder(sys.modules[__name__])

# flask-login 에서 사용
mpb.addProp("loadUser", lambda: _load_user) 

# 다른 모듈에서 _db:SQLAlchemy 인스턴스를 접근하는데 사용
# ex) from db import db as DB
# 이 모듈 로딩시의 _db값(=None)이 아닌 import호출시 값을 리턴(C#의 property)
mpb.addProp("db", lambda: _db)


# endregion
