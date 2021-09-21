"""센서데이터 모델 정의 및 관련 로직"""

# from types import LambdaType
# from typing import Dict
# from db.imports import *


# class SensorData(db.Model):
#     """센서 데이터의 DB 모델"""

#     # 기존 DBMS에서 정보를 추출하여 생성
#     # __table__ = sc.Table(
#     def _reflect() -> sc.Table:
#         return sc.Table(
#             "sensor_data",
#             db.Model.metadata,
#             #
#             # TimescaleDB hypertable 제약조건과 SqlAlchemy의 제약조건간 충돌
#             #  -> id 컬럼에 PK 속성을 추가
#             # TODO: sqlalchemy에서 id 컬럼 없이 동작? -->No
#             #
#             sc.Column("id", st.Integer, primary_key=True, autoincrement="auto"),
#             #
#             autoload_with=db.engine,
#         )
#         # TODO: relationship?

#     __table__ = _reflect()
#     # ---

#     def __repr__(self):
#         return f"<SensorData: {self.sensor_id}@{self.time}>"

#     def to_dict(self):
#         """인스턴스 객체의 dict 표현을 구한다"""

#         keys = self.__table__.columns.keys()
#         dic = {key: self.__getattribute__(key) for key in keys}
#         return dic


# # 모듈 함수 추가
# ActionBuilder[SensorData](sys.modules[__name__], SensorData)
