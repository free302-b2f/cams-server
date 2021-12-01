"""로그인 사용자 모델 정의 및 관련 로직"""

print(f"<{__name__}> loading...")

from ._imports import *
import sys
import flask as fl
import flask_login as fli
import werkzeug.security as wsec

dba = fl.g.dba

class AppUser(fli.UserMixin, dba.Model):
    """로그인 사용자 DB모델"""

    # region ---- View에서 사용할 필드 정보 ----
    # 클래스 변수: 각 필드 최대 길이 등
    max_username = 32
    max_email = 64
    max_password = 32
    max_password_hash = 182
    max_realname = 64

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
    realname = dba.Column(dba.String(max_realname))
    level = dba.Column(dba.Integer, nullable=False, server_default="-1") # 현재 일반유저 TODO: -1로 변경
    group_id = dba.Column(dba.Integer, dba.ForeignKey("app_group.id"), nullable=False)
    group = dba.relationship("Group", backref=dba.backref("users", lazy=True))
    # Column('version', Integer, server_default="SELECT MAX(1, MAX(old_versions)) FROM version_table")
    # -3=탈퇴(삭제예정), -2=잠금(로그인 불가), -1=게스트, 0=일반, +1=그룹관리자, +2=마스터
    # 마스터: 아이디 승인/관리, 모든 데이터 관리 가능
    # 그룹관리자: 그룹 일반 아이디 승인/관리, 그룹 소속 데이터 관리, 그룹당 1개
    # 일반: 그룹 데이터 접근(읽기전용)
    # 게스트: 로그인 가능, 그룹 없음, 그룹 관리자의 가입승인 필요 <-- 최초가입시 상태
    # 잠금: 로그인 불가

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
