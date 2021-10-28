"""WebApp 기본 데이터를 DB에 추가
+ 관리자 계정
+ 추가계정 : pheno
  - farm 
  - sensor
TODO: app_settings.json에서 불러오도록
"""

from datetime import date, datetime, time, timedelta, timezone
import flask as fl
import werkzeug.security as wsec

#! import all models
from db.user import AppUser
from db.farm import Farm
from db.sensor import Sensor
from db.admin import Cams

dba = fl.g.dba

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
farm.sensors.append(
    Sensor(sn="B2F_CAMs_2000000000003", name="Test Sensor", desc="DrBAE's Test CAMs")
)
user.farms.append(farm)
dba.session.add(user)

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
dba.session.add(user)

# 관리 정보 추가
dba.session.add(Cams("cams_setup_date", datetime.utcnow().isoformat()))
dba.session.add(Cams("cams_start_date", datetime.utcnow().isoformat()))
dba.session.commit()

# 랜덤 센서 데이터 추가
from .sensor_data import f2_init_and_seed

f2_init_and_seed()
