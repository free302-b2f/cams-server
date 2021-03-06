"""장소 모델 정의 및 관련 로직"""

print(f"<{__name__}> loading...")

from ._imports import *
import flask as fl
import sys

dba = fl.g.dba


class Location(dba.Model):
    """장소 DB 모델"""

    # region ---- View에서 사용할 필드 정보 ----
    # 클래스 변수: 각 필드 최대 길이 등
    max_name = 64
    max_desc = 64

    @classmethod
    def max_len(cls):
        """각 필드의 최대길이를 리턴"""

        return {
            "max_name": cls.max_name,
            "max_desc": cls.max_desc,
        }

    # endregion

    # 테이블 컬럼 정의
    __tablename__ = "location"
    id = dba.Column(dba.Integer, primary_key=True)
    name = dba.Column(dba.String(max_name), nullable=False)
    desc = dba.Column(dba.String(max_desc), nullable=False)
    group_id = dba.Column(dba.Integer, dba.ForeignKey("app_group.id"), nullable=False)
    group = dba.relationship("Group", backref=dba.backref("locations", lazy=True))
    __table_args__ = (dba.UniqueConstraint(group_id, name),)

    def __repr__(self):
        return f"<Location: [{self.id}] {self.name}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic


if getattr(sys, "_test_", None):
    farm = Location()
    print(f"{Location.max_len()= }")
    print(f"{farm.to_dict()= }")
