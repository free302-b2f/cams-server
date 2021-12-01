"""KIST 메타 데이터 추가"""

if __name__ == "__main__":
    import sys, os

    dir = os.path.dirname(__file__)
    __package__ = os.path.basename(dir)
    sys.path.append(os.path.dirname(dir))
    # 이렇게 하면 상대경로 임포트시 ImportError는 나지 않지만
    # db.__init__.py이 로딩되며 
    # 결국 flask.current_app가 필요하다.

from datetime import date, datetime, time, timedelta, timezone
import flask as fl
import werkzeug.security as wsec
from flask_sqlalchemy import SQLAlchemy
import json

#! import all models
from .group import Group
from .user import AppUser
from .location import Location
from .sensor import Sensor
from .admin import Cams
import utility as util


def dump_json(filename):
    """추가할 메타데이터를 json으로 저장"""

    dba: SQLAlchemy = fl.g.dba

    # add group
    group = Group(name="PHENO", desc="KIST Pheno Project")

    # add user
    pw = util.generate_password_hash("kist1966!!!")
    user = AppUser(
        username="pheno",
        password=pw,
        email="kist-pheno@gmail.com",
        realname="Pheno KIST",
        level=1,  # group admin
    )
    group.users.append(user)

    # add location
    loc = Location(name="제1동 제1구역", desc="2021년 12월 작물1")
    group.locations.append(loc)

    # add sensor
    sensors = [
        Sensor(
            sn=f"B2F_CAMs_100000000000{i}", name=f"Sensor {i}", desc=f"KIST CAMs #{i}"
        )
        for i in range(1, 7)
    ]
    loc.sensors.extend(sensors)
    group.sensors.extend(sensors)

    # TEST: json dump all seed data
    dic = {"group": group.to_dict()}
    dic["user"] = [u.to_dict() for u in group.users]
    dic["location"] = [l.to_dict() for l in group.locations]

    for i in range(len(group.locations)):
        dic[f"sensor{i}"] = [s.to_dict() for s in group.locations[i].sensors]

    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(dic, fp, indent=4, ensure_ascii=False)

    print(f"json dump: {filename}")


# if __name__ == "__main__":
#     # flask.app 필요
#     dump_json()
