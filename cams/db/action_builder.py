"""db패키지의 각 모듈에 모델의 연산을 수행하는 함수를 추가하는 도움클래스"""

from types import ModuleType
from typing import List, Generic, TypeVar

from db import db

M = TypeVar("M", db.Model, db.Model)


class ActionBuilder(Generic[M]):
    """주어진 모듈에 주어진 DB모델의 연산을 수행하는 함수를 정의한다.

    ** 다음과 같은 메소드를 정의한다.
    + list(): DB에서 주어진 모델의 레코드 목록을 추출한다.
    + insert(): 모델의 새 레코드를 DB에 추가한다.
    + getBy(): 주어진 필터링 조건에 맞는 첫번째 레코드를 추출한다."""

    def __init__(self, module: ModuleType, m: M) -> None:
        """인스턴스 객체 생성

        :param m: 연산할 대상 모델의 클래스 ex) db.user.User
        """

        self.module = module
        self.m = m

        module.list = self.list
        module.insert = self.insert
        module.getBy = self.getBy

        pass

    def list(self) -> List[M]:
        """사용자 목록 리턴"""

        return self.m.query.all()

    def insert(self, **kwargs) -> M:
        """새 사용자 추가"""

        model = self.m(**kwargs)
        db.session.add(model)
        db.session.commit()
        return model

    def getBy(self, **kwargs) -> M:
        """주어진 조건의 사용자 추출"""

        model = self.m.query.filter_by(**kwargs).first()
        return model
