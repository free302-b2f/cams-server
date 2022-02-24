"""센서 모델 정의 및 관련 로직"""

print(f"<{__name__}> loading...")

from ._imports import *
import flask as fl
import sys

dba = fl.g.dba


class Sensor(dba.Model):
    """센서 DB 모델"""

    # region ---- View에서 사용할 필드 정보 ----
    # 클래스 변수: 각 필드 최대 길이 등
    max_sn = 32
    max_name = 64

    @classmethod
    def max_len(cls):
        """각 필드의 최대길이를 리턴"""

        return {
            "max_sn": cls.max_sn,
            "max_name": cls.max_name,
        }

    # endregion

    # 테이블 컬럼 정의
    __tablename__ = "sensor"
    id = dba.Column(dba.Integer, primary_key=True)
    sn = dba.Column(dba.String(max_sn), nullable=False, unique=True)
    name = dba.Column(dba.String(max_name), nullable=False)
    location_id = dba.Column(dba.Integer, dba.ForeignKey("location.id"), nullable=False)
    location = dba.relationship("Location", backref=dba.backref("sensors", lazy=True))
    group_id = dba.Column(dba.Integer, dba.ForeignKey("app_group.id"), nullable=False)
    group = dba.relationship("Group", backref=dba.backref("sensors", lazy=True))
    __table_args__ = (dba.UniqueConstraint(group_id, name),)

    def __repr__(self):
        return f"<Sensor: [{self.id}] {self.name}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic


if getattr(sys, "_test_", None):
    sensor = Sensor()
    print(f"{Sensor.max_len()= }")
    print(f"{sensor.max_len()= }")
    print(f"{sensor.to_dict()= }")
