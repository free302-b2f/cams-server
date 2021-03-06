"""조직 모델 정의 및 관련 로직"""

print(f"<{__name__}> loading...")

from ._imports import *
import flask as fl
import sys

dba = fl.g.dba


class Group(dba.Model):
    """조직 DB 모델"""

    # region ---- View에서 사용할 필드 정보 ----
    # 클래스 변수: 각 필드 최대 길이 등
    max_name = 64
    max_desc = 64

    @classmethod
    def max_len(cls):
        """각 필드의 최대길이를 리턴"""

        return {
            "max_group_name": cls.max_name,
            "max_group_desc": cls.max_desc,
        }

    # endregion

    # 테이블 컬럼 정의
    __tablename__ = "app_group"
    id = dba.Column(dba.Integer, primary_key=True)
    name = dba.Column(dba.String(max_name), nullable=False, unique=True)
    desc = dba.Column(dba.String(max_desc), nullable=False)
    storage_id = dba.Column(dba.Integer, server_default="0")
    # location_id: 그룹의 유휴센서보관소 Location의 id
    # 각 그룹은 고유의 유휴센서보관소 Location을 갖는다

    def __repr__(self):
        return f"<Group: [{self.id}] {self.name}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic

    @classmethod
    def reset_id_seq(cls, id):
        """id의 시퀀스를 재설정한다"""

        seq = f"{cls.__tablename__}_id_seq"
        dba.session.execute(f"ALTER SEQUENCE {seq} RESTART WITH {id + 1}")
        # next = dba.session.execute(f"SELECT nextval('{seq}')").fetchone()


if getattr(sys, "_test_", None):
    group = Group()
    print(f"{Group.max_len()= }")
    print(f"{group.to_dict()= }")
    # print(f"{Group.guest().to_dict()= }")
