"""로그인 사용자 모델 정의 및 관련 로직"""

from db.imports import *

import flask_login as fli
import werkzeug.security as wsec


class AppUser(fli.UserMixin, db.Model):
    """로그인 사용자 DB모델"""

    # region ---- View에서 사용할 필드 정보 ----
    # 클래스 변수: 각 필드 최대 길이 등
    max_username = 32
    max_email = 64
    max_password = 32
    max_password_hash = 88
    max_realname = 32

    @classmethod
    def max_len(cls):
        """각 필드의 최대길이를 리턴"""

        return {
            "max_username": cls.max_username,
            "max_password": cls.max_password,
            "max_email": cls.max_email,
            "max_password_hash": cls.max_password_hash,
            "max_realname": cls.max_realname,
        }

    # endregion

    # 테이블 컬럼 정의
    __tablename__ = "app_user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(max_username), unique=True, nullable=False)
    email = db.Column(db.String(max_email), unique=True)
    password = db.Column(db.String(max_password_hash))
    realname = db.Column(db.String(max_password_hash))

    def __repr__(self):
        return f"<User: {self.username}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic

