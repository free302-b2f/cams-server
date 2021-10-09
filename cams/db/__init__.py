"""패키지 초기화
 + __all__ 정의
 + SQLAlchemy DB 초기화
 """

# region ---- __all__ 정의 ----

__all__ = ["user", "farm", "sensor", "sensor_data", "admin", "init"]

# endregion


# region ---- imports ----

import sys, json
from datetime import timedelta, datetime, timezone, time
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
_dba: SQLAlchemy = None

# endregion


# region ---- app 초기화 ----


def init_app(server: fl.Flask) -> fli.LoginManager:
    """server 설정 및 로그인메니저 생성"""

    server.config.update(
        SQLALCHEMY_DATABASE_URI=_dbUri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    global _dba, _seed_meta

    #! db.xxx 모듈을 실행하기 전에 _dba 초기화 필요
    _dba = SQLAlchemy(server)
    # _dba.Model.metadata.reflect(bind=_dba.engine, schema=_set["Db"])

    #! import all models
    from db.user import AppUser
    from db.farm import Farm
    from db.sensor import Sensor
    from db.admin import Cams

    # create all model tables & seed
    if _set["DropTables"]:
        from db.sensor_data import f0_drop_sensor_data

        f0_drop_sensor_data()
        _dba.drop_all()
        # _db.Model.metadata.bind = _db.engine # drop_all()시 불필요
        # Sensor.__table__.drop(checkfirst=True)
        # Farm.__table__.drop(checkfirst=True)
        # User.__table__.drop(checkfirst=True)

        _dba.create_all()
        _seed_meta()

    pass  # init_app


def _seed_meta():
    import werkzeug.security as wsec
    from db.sensor_data import f2_init_and_seed

    #! import all models
    from db.user import AppUser
    from db.farm import Farm
    from db.sensor import Sensor
    from db.admin import Cams

    # drbae + test farm + test sensor
    pw = wsec.generate_password_hash("3569", method="sha256")
    user = AppUser(
        username="drbae",
        password=pw,
        email="amadeus.bae@gmail.com",
        realname="Samyong Bae",
        level=1,  # administrator
    )
    farm = Farm(name="B2F Test Farm")
    farm.sensors.append(Sensor(sn="B2F_CAMs_1000000000003", name="Test Sensor"))
    user.farms.append(farm)
    _dba.session.add(user)

    # KIST Pheno
    pw = wsec.generate_password_hash("kist1966!!!", method="sha256")
    user = AppUser(
        username="pheno",
        password=pw,
        email="kist-pheno@gmail.com",
        realname="Pheno KIST",
        level=0,
    )
    farm = Farm(name="KIST Pheno Farm")
    farm.sensors.append(Sensor(sn="B2F_CAMs_1000000000001", name="Lab Sensor 1"))
    farm.sensors.append(Sensor(sn="B2F_CAMs_1000000000002", name="Lab Sensor 2"))
    user.farms.append(farm)
    _dba.session.add(user)

    # 관리 정보 추가
    _dba.session.add(Cams("cams_setup_date", datetime.utcnow().isoformat()))
    _dba.session.add(Cams("cams_start_date", datetime.utcnow().isoformat()))

    _dba.session.commit()

    f2_init_and_seed()

# endregion

def get_dba():
    if not _dba:
        raise ValueError(f"{__name__}._dba == None")
    return _dba