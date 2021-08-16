"""로그인 사용자 모델 정의 및 관련 로직"""

from db.imports import *

import flask_login as fli
import werkzeug.security as wsec


class User(fli.UserMixin, db.Model):
    """로그인 사용자 DB모델"""

    max_username = 32
    max_email = 64
    max_password = 32
    max_password_hash = 88

    # 테이블 컬럼 정의
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(max_username), unique=True, nullable=False)
    email = db.Column(db.String(max_email), unique=True)
    password = db.Column(db.String(max_password_hash))

    def __repr__(self):
        return f"<User {self.username}>"


class _UserAction(ActionBuilder[User]):
    """db.user 모듈의 insert() 함수를 오버라이딩하는 클래스"""

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
