"""WebApp 기본 데이터를 DB에 추가
+ 관리자 계정
+ json
"""

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
from .cams_info import Cams


def seed():
    """DB 작업 수행"""

    dba: SQLAlchemy = fl.g.dba

    # 관리 정보 추가
    dba.session.add(Cams("cams_setup_date", datetime.now().isoformat()))
    dba.session.add(Cams("cams_start_date", datetime.now().isoformat()))
    dba.session.commit()

    # ----[ 마스터 계정 ]----
    from . import _seed_master

    _seed_master.seed()

    # ----[ KIST Pheno ]----
    from . import _seed_kist

    kist_json = "seed-kist-pheno.json"
    # _seed_kist.dump_json(kist_json) # save to json file
    load_json_seed(kist_json)  # load from json file


# json 파일에서 읽어와 DB에 추가
def load_json_seed(filename: str):
    """json 파일에서 메타데이터를 읽어들여 DB에 추가"""

    # read json
    dic = {}
    with open(filename, "r", encoding="utf-8") as fp:
        dic.update(json.load(fp))

    # add group
    jGroup = dic["group"]
    group = Group(name=jGroup["name"], desc=jGroup["desc"])

    # add user
    for i, jUser in enumerate(dic["user"]):
        user = AppUser(
            username=jUser["username"],
            password=jUser["password"],
            email=jUser["email"],
            realname=jUser["realname"],
            level=jUser["level"],
        )
        group.users.append(user)

    # add location
    for i, jLoc in enumerate(dic["location"]):
        loc = Location(name=jLoc["name"], desc=jLoc["desc"])
        for jS in dic[f"sensor{i}"]:
            loc.sensors.append(Sensor(sn=jS["sn"], name=jS["name"]))
        group.locations.append(loc)
        group.sensors.extend(loc.sensors)

    dba: SQLAlchemy = fl.g.dba
    dba.session.add(group)
    dba.session.commit()
