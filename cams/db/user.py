"""로그인 사용자 모델 정의 및 관련 로직"""

from db._imports import *

import flask_login as fli
import werkzeug.security as wsec


class AppUser(fli.UserMixin, dba.Model):
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
    id = dba.Column(dba.Integer, primary_key=True)
    username = dba.Column(dba.String(max_username), unique=True, nullable=False)
    email = dba.Column(dba.String(max_email), unique=True)
    password = dba.Column(dba.String(max_password_hash))
    realname = dba.Column(dba.String(max_password_hash))
    level = dba.Column(dba.Integer, nullable=False, default=0) # 현재 일반유저 TODO: -1로 변경
    # Column('version', Integer, server_default="SELECT MAX(1, MAX(old_versions)) FROM version_table")
    # -2=잠금, -1=게스트, 0=일반, +1=관리자
    # 관리자~아이디 승인/관리, 모든 팜/센서 접근()
    # 일반~소유 팜/센서만 접근
    # 게스트~팜/센서 소유/접근 불가, 로그인 가능  <-- 최초가입시 상태
    # 잠금~로그인 불가

    def __repr__(self):
        return f"<User: {self.username}>"

    def to_dict(self):
        """인스턴스 객체의 dict 표현을 구한다"""

        keys = self.__table__.columns.keys()
        dic = {key: self.__getattribute__(key) for key in keys}
        return dic


if getattr(sys, "_test_", None):
    user = AppUser()
    print(f"{AppUser.max_len()= }")
    print(f"{user.to_dict()= }")
