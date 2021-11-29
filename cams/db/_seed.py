"""WebApp 기본 데이터를 DB에 추가
+ 관리자 계정
+ json
"""

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


# 관리 정보 추가
dba.session.add(Cams("cams_setup_date", datetime.utcnow().isoformat()))
dba.session.add(Cams("cams_start_date", datetime.utcnow().isoformat()))
dba.session.commit()

# 마스터 계정
from . import _seed_master

# json 파일에서 읽어와 DB에 추가
def _load_json_seed(filename: str):
    import json

    dic = {}
    with open(filename, "r", encoding="utf-8") as fp:
        dic.update(json.load(fp))

    jUser = dic["user"]
    user = AppUser(
        username=jUser["username"],
        password=jUser["password"],
        email=jUser["email"],
        realname=jUser["realname"],
        level=jUser["level"],
    )

    for i, jFarm in enumerate(dic["farm"]):
        farm = Farm(name=jFarm["name"])
        for js in dic[f"sensor{i}"]:
            farm.sensors.append(Sensor(sn=js["sn"], name=js["name"], desc=js["desc"]))
        user.farms.append(farm)

    dba.session.add(user)
    dba.session.commit()


# KIST Pheno
# from . import _seed_kist as kist
# kist.export_json()

_load_json_seed("kist-seed.json")
