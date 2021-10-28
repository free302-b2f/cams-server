"""관리용 테이블 모델 및 기타 유틸"""

print(f"<{__name__}> loading...")

from ._imports import *
import flask as fl
import sys

dba = fl.g.dba

class Cams(dba.Model):
    """관리용 모델 - dict 형식으로 각 row는 하나의 키-값 쌍에 해당"""

    # region ---- View에서 사용할 필드 정보 ----
    # 클래스 변수: 각 필드 최대 길이 등
    max_key = 1024
    # max_json = 1024 * 1024 * 1024  # 1GiB

    @classmethod
    def max_len(cls):
        """각 필드의 최대길이를 리턴"""
        return {
            "max_key": cls.max_key,
            # "max_json": cls.max_json,
        }

    # endregion

    # 테이블 컬럼 정의
    __tablename__ = "cams"
    id = dba.Column(dba.Integer, primary_key=True)
    key = dba.Column(dba.String(max_key), nullable=False)  # 키
    text = dba.Column(dba.Text(), nullable=True)  # 객체를 직렬화 저랑

    def __init__(self, key: str, text: str):
        self.key = key
        self.text = text

    def __repr__(self):
        return f"<Cams: {self.key}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic


if getattr(sys, "_test_", None):
    cams = Cams("abc", "ABC")
    print(f"{Cams.max_len()= }")
    print(f"{cams.to_dict()= }")
