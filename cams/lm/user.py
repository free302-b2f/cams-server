'''로그인 사용자 모델 정의 및 관련 로직'''

from lm.imports import *


class User(fli.UserMixin, db.Model):
    """로그인 사용자 모델"""

    max_username = 32
    max_email = 64
    max_password = 32

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(88))

    def __repr__(self):
        return f'<User {self.username}>'
