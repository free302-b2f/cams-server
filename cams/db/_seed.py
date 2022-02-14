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
import utility as util

# seed data files
SEED_MASTER_FILE = "seed-master.json"  # 마스터 계정과 테스트용 센서 추가


def seed():
    """DB 작업 수행"""

    dba: SQLAlchemy = fl.g.dba

    # 관리 정보 추가
    dba.session.add(Cams("cams_setup_date", datetime.now().isoformat()))
    dba.session.add(Cams("cams_start_date", datetime.now().isoformat()))
    dba.session.commit()

    # ----[ 비투팜 그룹 & 마스터 계정 ]----
    groups = seed_group_json(SEED_MASTER_FILE)
    from . import sensor_data as sd

    for group in groups:
        sd.f3_seed(group.sensors)  # 랜덤 센서 데이터 추가

    # ----[ 추가 그룹 ]----
    fn = fl.g.settings["Cams"]["SEED_FILE"]
    seed_group_json(fn)


# json 파일에서 읽어와 DB에 추가
def seed_group_json(filename: str) -> Group:
    """json 파일에서 group을 읽어들여 DB에 추가"""

    # read json
    with open(filename, "r", encoding="utf-8") as fp:
        dics = json.load(fp)

    groups = []
    for dic in dics:
        # add group
        group = Group(name=dic["name"], desc=dic["desc"])

        # add user
        for jUser in dic["users"]:
            pw = jUser["password"]
            pwHash = pw if pw.startswith("pbkdf2:") else util.generate_password_hash(pw)
            user = AppUser(
                username=jUser["username"],
                password=pwHash,
                email=jUser["email"],
                realname=jUser["realname"],
                level=jUser["level"],
            )
            group.users.append(user)

        # add location
        for jLoc in dic["locations"]:
            loc = Location(name=jLoc["name"], desc=jLoc["desc"])
            for jS in jLoc["sensors"]:
                loc.sensors.append(Sensor(sn=jS["sn"], name=jS["name"]))
            group.locations.append(loc)
            group.sensors.extend(loc.sensors)

        dba: SQLAlchemy = fl.g.dba
        dba.session.add(group)
        dba.session.commit()

        groups.append(group)

    return groups


def save_groups_json(groups, filename):
    """group 리스트를 json 파일에 저장"""

    dic = [_group_to_dic(group) for group in groups]

    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(dic, fp, indent=4, ensure_ascii=False)

    util.info(f"{filename} saved")


def _group_to_dic(group):
    """group을 json 직렬화에 적합한 dict으로 변환"""

    dic = group.to_dict()
    dic["users"] = [u.to_dict() for u in group.users]

    locs = []
    for l in group.locations:
        locDic = l.to_dict()
        locDic["sensors"] = [s.to_dict() for s in l.sensors]
        locs.append(locDic)

    # python3.9: z = x|y
    dic["locations"] = [
        {**l.to_dict(), **{"sensors": [s.to_dict() for s in l.sensors]}}
        for l in group.locations
    ]

    dic = _clean_nones(dic)
    return dic
    # return json.dumps(dic, indent=4, ensure_ascii=False)


def _clean_nones(value):
    """리스트와 사전에서 None값을 제거하여 새 객체 리턴"""

    # 리스트
    if isinstance(value, list):
        return [_clean_nones(x) for x in value if x is not None]

    # 사전
    elif isinstance(value, dict):
        return {key: _clean_nones(val) for key, val in value.items() if val is not None}

    # 그외값
    else:
        return value
