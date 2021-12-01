"""패키지 초기화
 + __all__ 정의
 + Flask 인스턴스 생성시 1번 실행 - SQLAlchemy인스턴스/모델정의
 """

print(f"<{__name__}> loading...")

# __all__ = ["user", "farm", "sensor", "sensor_data", "admin"]
__all__ = []

from datetime import date, datetime, time, timedelta, timezone
import flask as fl
from utility import loadAppSettings, debug, error, info
from flask_sqlalchemy import SQLAlchemy

_app = fl.current_app
_set = loadAppSettings("Postgres")
_dbUri = (
    f'postgresql://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)

_app.config.update(
    SQLALCHEMY_DATABASE_URI=_dbUri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    POSTGRESQL_URI=_dbUri,
    # _dba.Model.metadata.reflect(bind=_dba.engine, schema=_set["Db"])
)
_app.config.update(SQLALCHEMY_INSTANCE=SQLAlchemy(_app))


@_app.before_request
def before_request():
    """모든 요청 전에 SQLAlchemy를 fl.g에 추가"""

    fl.g.dba = _app.config["SQLALCHEMY_INSTANCE"]
    # debug("db.before_request()")

    pass


@_app.teardown_appcontext
def teardown_appcontext(ex):
    """ """

    # debug("db.teardown_appcontext()")

    # sqlalchemy 는 자동으로 종료처리한다
    # dba = fl.g.pop("dba", None)
    # if dba:
    #     dba.close()

    pass


# Build Models - import all models
# *** DO NOT import sensor_data ***
before_request()

from . import group
from . import user
from . import location
from . import sensor
from . import admin

# from db.user import AppUser
# from db.farm import Farm
# from db.sensor import Sensor
# from db.admin import Cams

# create all model tables & seed
if _set["DropTables"]:

    # TODO: DO NOT drop sensor_data: data never die!
    # from db.sensor_data import f1_drop_table, f1_clear_data, f2_create_table
    from . import sensor_data as sd

    sd.f1_drop_table()
    # f0_clear_sensor_data()

    dba: SQLAlchemy = fl.g.dba
    dba.drop_all()
    # _db.Model.metadata.bind = _db.engine # drop_all()시 불필요
    # Sensor.__table__.drop(checkfirst=True)
    # Farm.__table__.drop(checkfirst=True)
    # User.__table__.drop(checkfirst=True)

    dba.create_all()
    dba.session.commit()
    sd.f2_create_table()

    # seed meta data
    from . import _seed

    _seed.seed()
