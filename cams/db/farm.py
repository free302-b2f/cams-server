"""농장 모델 정의 및 관련 로직"""

from db.imports import *


class Farm(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(max_name), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False)
    user = db.relationship("AppUser", backref=db.backref("farms", lazy=True))

    def __repr__(self):
        return f"<Farm: {self.name}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic

