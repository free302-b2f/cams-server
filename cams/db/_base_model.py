"""모든 DB 모델의 베이스 모델을 정의 & 테스트"""
#
# TODO: 현재 실패... 각 테이블이 foreign key를 못찾음
#

from sqlalchemy.orm import declarative_mixin
from sqlalchemy.orm import declared_attr
from db import dba  # sqlalchemy ~ init_app() 실행된


@declarative_mixin
class BaseModel(object):
    """베이스 모델: id 필드 생성, to_dict() 구현"""

    # region ---- 클래스 속성/변수/메소드 ----

    # # 각 필드의 최대길이, 뷰에서 사용
    __maxlen__ = {}  # TODO: 상속 클래스에서 이 속성을 업데이트

    @declared_attr
    def max_len(cls):
        """각 가변길이 필드의 최대길이를 dict형태로 리턴"""

        return cls.__maxlen__

    # # 테이블 이름 정의
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # endregion ----

    # 모든 테이블의 공통 필드 정의
    id = dba.Column(dba.Integer, primary_key=True)

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic


# ~ class

# run test~
import sys

if getattr(sys, "_test_", None):

    class TestModel(BaseModel, dba.Model):
        """상속 클래스에서의 사용 예시"""

        max_key = 32
        # BaseModel.__maxlen__.update(
        #     {
        #         "max_key": max_key,
        #     }
        # )
        
        key = dba.Column(dba.String(max_key), nullable=False)  # 키
        pass

    def test():
        m = TestModel()

        try:
            TestModel.max_len()
        except TypeError as ex:
            print(f"{ex= }")

        print(f"{m.max_len= }")
        print(f"{m.to_dict()= }")
        pass

    test()
