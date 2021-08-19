"""센서데이터 모델 정의 및 관련 로직"""

from types import LambdaType
from typing import Dict
from db.imports import *


class SensorData(db.Model):
    """센서 데이터의 DB 모델"""

    def _reflect() -> sc.Table:
        return sc.Table(
            "sensor_data",
            db.Model.metadata,
            #
            # TimescaleDB hypertable 제약조건과 SqlAlchemy의 제약조건간 충돌
            #  -> id 컬럼에 PK 속성을 추가
            # TODO: sqlalchemy에서 id 컬럼 없이 동작?
            #
            sc.Column("id", st.Integer, primary_key=True, autoincrement="auto"),
            #
            autoload_with=db.engine,
        )

    __table__ = _reflect()
    _keys = __table__.columns.keys()

    def __repr__(self):
        return f"<SensorData {self.sensor_id}@{self.time}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        dic = {key: self.__getattribute__(key) for key in self._keys}
        return dic


ActionBuilder[SensorData](sys.modules[__name__], SensorData)
