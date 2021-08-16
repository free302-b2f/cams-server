"""로그인 사용자 모델 정의 및 관련 로직"""

import flask_login as fli
from db import db


class User(fli.UserMixin, db.Model):
    """로그인 사용자 모델"""

    max_username = 32
    max_email = 64
    max_password = 32
    max_password_hash = 88

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(max_username), unique=True, nullable=False)
    email = db.Column(db.String(max_email), unique=True)
    password = db.Column(db.String(max_password_hash))

    def __repr__(self):
        return f"<User {self.username}>"
