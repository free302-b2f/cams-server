"""농장 모델 정의 및 관련 로직"""

from db.imports import *


class Farms(db.Model):
    """농장 DB 모델"""

    # 상수
    max_name = 64

    # 테이블 컬럼 정의
    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    name = db.Column(db.String(max_name), unique=True, nullable=False)

    def __repr__(self):
        return f"<Farm {self.name}>"


# 모듈 함수 추가
ActionBuilder[Farms](sys.modules[__name__], Farms)
