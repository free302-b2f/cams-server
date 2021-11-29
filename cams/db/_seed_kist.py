"""KIST 메타 데이터 추가"""

from datetime import date, datetime, time, timedelta, timezone
import flask as fl
import werkzeug.security as wsec
from flask_sqlalchemy import SQLAlchemy
import json

#! import all models
from .user import AppUser
from .farm import Farm
from .sensor import Sensor
from .admin import Cams

dba: SQLAlchemy = fl.g.dba


def dump_json():
    pw = wsec.generate_password_hash("kist1966!!!", method="sha256")
    user = AppUser(
        username="pheno",
        password=pw,
        email="kist-pheno@gmail.com",
        realname="Pheno KIST",
        level=1,
    )
    farm = Farm(name="Pheno 구역 #1")
    farm.sensors.append(
        Sensor(sn="B2F_CAMs_1000000000001", name="Lab Sensor 1", desc="KIST CAMs #1")
    )
    farm.sensors.append(
        Sensor(sn="B2F_CAMs_1000000000002", name="Lab Sensor 2", desc="KIST CAMs #2")
    )
    farm.sensors.append(
        Sensor(sn="B2F_CAMs_1000000000003", name="Lab Sensor 3", desc="KIST CAMs #3")
    )
    farm.sensors.append(
        Sensor(sn="B2F_CAMs_1000000000004", name="Lab Sensor 4", desc="KIST CAMs #4")
    )
    farm.sensors.append(
        Sensor(sn="B2F_CAMs_1000000000005", name="Lab Sensor 5", desc="KIST CAMs #5")
    )
    farm.sensors.append(
        Sensor(sn="B2F_CAMs_1000000000006", name="Lab Sensor 6", desc="KIST CAMs #6")
    )
    user.farms.append(farm)

    # TEST: json dump all seed data
    dic = {}    
    dic["user"] = user.to_dict()
    dic["farm"] = [f.to_dict() for f in user.farms]

    for i in range(len(user.farms)):
        # dic[f"farm{i}"] = f.to_dict()
        dic[f"sensor{i}"] = [s.to_dict() for s in user.farms[i].sensors]

    with open("kist-seed.json", "w", encoding="utf-8") as fp:
        json.dump(dic, fp, indent=4, ensure_ascii=False)

    print("json dump")


