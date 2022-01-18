"""마스터계정 추가, 테스트 센서 추가"""

from datetime import date, datetime, time, timedelta, timezone
import flask as fl
import werkzeug.security as wsec
from flask_sqlalchemy import SQLAlchemy

#! import all models
from .group import Group
from .user import AppUser
from .location import Location
from .sensor import Sensor
from .cams_info import Cams
import utility as util


def seed():
    """추가: 마스터 계정 및 테스트 센서"""

    dba: SQLAlchemy = fl.g.dba

    # add group
    group = Group(name="TEST", desc="개발 테스트 농장")

    # add user
    user = AppUser(
        username="cams",
        password=util.generate_password_hash("1q2w#E$R"),
        email="amadeus.bae@gmail.com",
        realname="B2F Master",
        level=2,  # master
    )
    group.users.append(user)

    # add location
    loc = Location(name="제1구역", desc="물토란(2021년 12월)")
    group.locations.append(loc)

    # add sensor
    sensors = [
        Sensor(sn=f"B2F_CAMs_200000000000{i}", name=f"DrBAE's CAMs #{i}")
        for i in range(1, 3)
    ]
    loc.sensors.extend(sensors)
    group.sensors.extend(sensors)

    dba.session.add(group)
    dba.session.commit()

    # 랜덤 센서 데이터 추가
    from . import sensor_data as sd

    sd.f3_seed(sensors)
