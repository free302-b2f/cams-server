"""로그인 사용자 모델 정의 및 관련 로직"""

from db.imports import *

import flask_login as fli
import werkzeug.security as wsec


class User(fli.UserMixin, db.Model):
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
            "max_un": cls.max_username,
            "max_pw": cls.max_password,
            "max_em": cls.max_email,
            "max_pwd": cls.max_password_hash,
            "max_rn": cls.max_realname,
        }

    # endregion

    # 테이블 컬럼 정의
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


# region ---- 테이블 조작 연산 추가 -----
class _UserAction(ActionBuilder[User]):
    """db.user 모듈 ActionBuilder에 의해 정의된 함수를 오버라이딩하는 클래스"""

    # override insert()
    def insert(self, **kwargs) -> User:
        """오버라이드 - 패스워드 암호화 추가"""

        # encrypt plain password
        pw = wsec.generate_password_hash(kwargs["password"], method="sha256")
        kwargs["password"] = pw

        # 부모의 메소드 호출
        return ActionBuilder.insert(self, **kwargs)

    pass


# 모듈 함수 추가
_UserAction(sys.modules[__name__], User)

# endregion
