"""농장 모델 정의 및 관련 로직"""

print(f"<{__name__}> loading...")

from ._imports import *
import flask as fl
import sys

dba = fl.g.dba


class Farm(dba.Model):
    """농장 DB 모델"""

    # region ---- View에서 사용할 필드 정보 ----
    # 클래스 변수: 각 필드 최대 길이 등
    max_name = 64

    @classmethod
    def max_len(cls):
        """각 필드의 최대길이를 리턴"""

        return {
            "max_name": cls.max_name,
        }

    # endregion

    # 테이블 컬럼 정의
    __tablename__ = "farm"
    id = dba.Column(dba.Integer, primary_key=True)
    name = dba.Column(dba.String(max_name), nullable=False)
    user_id = dba.Column(dba.Integer, dba.ForeignKey("app_user.id"), nullable=False)
    user = dba.relationship("AppUser", backref=dba.backref("farms", lazy=True))

    def __repr__(self):
        return f"<Farm: {self.name}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic    


if getattr(sys, "_test_", None):
    farm = Farm()
    print(f"{Farm.max_len()= }")
    print(f"{farm.to_dict()= }")
