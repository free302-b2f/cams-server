"""센서 모델 정의 및 관련 로직"""

from db._imports import *


class Sensor(dba.Model):
    """센서 DB 모델"""

    # region ---- View에서 사용할 필드 정보 ----
    # 클래스 변수: 각 필드 최대 길이 등
    max_sn = 32
    max_name = 64
    max_desc = 128

    @classmethod
    def max_len(cls):
        """각 필드의 최대길이를 리턴"""

        return {
            "max_sn": cls.max_sn,
            "max_name": cls.max_name,
            "max_desc": cls.max_desc,
        }

    # endregion

    # 테이블 컬럼 정의
    __tablename__ = "sensor"
    id = dba.Column(dba.Integer, primary_key=True)
    sn = dba.Column(dba.String(max_sn), nullable=False)
    name = dba.Column(dba.String(max_name), nullable=False)
    desc = dba.Column(dba.String(max_desc), nullable=True)
    farm_id = dba.Column(dba.Integer, dba.ForeignKey("farm.id"), nullable=False)
    farm = dba.relationship("Farm", backref=dba.backref("sensors", lazy=True))

    def __repr__(self):
        return f"<Sensor: {self.sn}>"

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
