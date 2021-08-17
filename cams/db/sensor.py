"""센서 모델 정의 및 관련 로직"""

from db.imports import *


class Sensors(db.Model):
    """센서 DB 모델"""

    # 상수 정의
    max_sn = 32

    # 테이블 컬럼 정의
    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    sn = db.Column(db.String(max_sn), unique=True, nullable=False)

    def __repr__(self):
        return f"<Sensor {self.sn}>"

    def to_dict(self):
        dic = {}
        dic["id"] = self.id
        dic["sn"] = self.sn
        return dic


# 모듈 함수 추가
ActionBuilder[Sensors](sys.modules[__name__], Sensors)
