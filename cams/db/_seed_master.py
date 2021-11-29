"""마스터계정 추가, 테스트 센서 추가"""

from datetime import date, datetime, time, timedelta, timezone
import flask as fl
import werkzeug.security as wsec
from flask_sqlalchemy import SQLAlchemy

#! import all models
from .user import AppUser
from .farm import Farm
from .sensor import Sensor
from .admin import Cams

dba: SQLAlchemy = fl.g.dba


# 마스터 계정 및 테스트 센서
pw = wsec.generate_password_hash("1q2w#E$R", method="sha256")
user = AppUser(
    username="cams",
    password=pw,
    email="amadeus.bae@gmail.com",
    realname="B2F Master",
    level=2,  # administrator
)
farm = Farm(name="농장 구역 #1")
farm.sensors.append(
    Sensor(sn="B2F_CAMs_2000000000001", name="Test Sensor", desc="DrBAE's Test CAMs")
)
user.farms.append(farm)
dba.session.add(user)
dba.session.commit()

# 랜덤 센서 데이터 추가
from . import sensor_data as sd

sd.f3_seed()
