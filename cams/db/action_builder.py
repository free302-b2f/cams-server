"""db패키지의 각 모듈에 모델의 연산을 수행하는 함수를 추가하는 도움클래스"""

from types import ModuleType
from typing import Any, Dict, List, Generic, TypeVar
from db import db

# 제너릭 타입변수 선언
M = TypeVar("M", db.Model, db.Model)

# 제너릭 베이스 클래스
class ActionBuilder(Generic[M]):
    """주어진 모듈에 주어진 DB모델의 연산을 수행하는 함수를 정의한다.

    ** 다음과 같은 메소드를 정의한다.
    + insert(): 모델의 새 레코드를 DB에 추가한다.
    + all(): 모델의 레코드 목록을 추출한다.
    + allDict(): 모델의 레코드 목록을 추출후 dict로 변환한다.
    + firstBy(): 필터링 조건에 맞는 첫번째 레코드를 추출한다.
    + listBy(): 필터링 조건에 맞는 레코드의 목록을 추출한다.
    + listDictBy(): 필터링 조건에 맞는 레코드의 목록을 추출하여 dict로 변환한다.
    """

    def __init__(self, module: ModuleType, m: M) -> None:
        """인스턴스 객체 생성

        :param m: 연산할 대상 모델의 클래스 ex) db.user.User
        """

        self.module = module
        self.m = m

        # 추가 메소드
        module.insert = self.insert  #

        # 전부 추출 메소드
        module.all = self.all  # all records
        module.allDict = self.allDict

        # 필터링 메소드
        module.firstBy = self.firstBy  # first record
        module.listBy = self.listBy
        module.listDictBy = self.listDictBy

        pass

    def insert(self, **kwargs) -> M:
        """모델 M의 새 레코드 추가"""

        model = self.m(**kwargs)
        db.session.add(model)
        db.session.commit()
        return model

    def all(self) -> List[M]:
        """모델 M의 레코드 목록 리턴"""

        return self.m.query.all()

    def allDict(self) -> List[Dict[str, Any]]:
        """모델 M의 레코드의 dict 형 목록 리턴"""

        models = self.m.query.all()
        dics = [m.to_dict() for m in models]
        return dics

    def firstBy(
        self,
        id: int = None,
        filterBy: dict = None,
        filter: list = None,
        orderBy: list = None,
        limit: int = None,
    ) -> M:
        """주어진 조건에 맞는 첫번째 레코드 추출"""

        model = self.listBy(id, filterBy, filter, orderBy, limit).first()
        return model

    def listBy(
        self,
        id: int = None,
        filterBy: dict = None,
        filter: list = None,
        orderBy: list = None,
        limit: int = None,
    ) -> List[M]:
        """모델 M의 주어진 조건에 맞는 레코드 목록 리턴"""

        q = self.m.query
        if id:
            return self.m.query.get(id)
        if filterBy:
            q = q.filter_by(**filterBy)
        if filter:
            for f in filter:
                q = q.filter(f)
        if orderBy:
            for o in orderBy:
                q = q.order_by(o)

        if limit:
            q = q.limit(limit)

        return q

    def listDictBy(
        self,
        id: int = None,
        filterBy: dict = None,
        filter: list = None,
        orderBy: list = None,
        limit: int = None,
    ) -> List[Dict[str, Any]]:
        """모델 M의 주어진 조건에 맞는 레코드의 dict형 목록 리턴"""

        models = self.listBy(id, filterBy, filter, orderBy, limit)
        dics = [m.to_dict() for m in models]
        return dics
