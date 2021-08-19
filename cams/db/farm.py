"""농장 모델 정의 및 관련 로직"""

from db.imports import *


class Farms(db.Model):
    """농장 DB 모델"""

    # 상수
    max_name = 64

    __table__ = sc.Table(
        "farms",
        db.Model.metadata,
        autoload_with=db.engine,
    )
    _keys = __table__.columns.keys()

    def __repr__(self):
        return f"<Farm {self.name}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        dic = {key: self.__getattribute__(key) for key in self._keys}
        return dic


# 모듈 함수 추가
ActionBuilder[Farms](sys.modules[__name__], Farms)
