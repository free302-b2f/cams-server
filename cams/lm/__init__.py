"""패키지 초기화
+ __all__ 정의
+ 로그인매니저 초기화
"""

print(f"<{__name__}> loading...")

# __all__ = ["signup", "login", "logout", "profile", "status"]
__all__ = []


import flask as fl
import flask_login as fli
import utility as util


# region ---- LoginManager 초기화 ----
"""로그인메니저 생성 및 server 설정"""

_app = fl.current_app
_set = util.loadAppSettings("LoginManager")
_lm = fli.LoginManager()

_lm.init_app(_app)
_lm.login_view = "/login"
_lm.signup_view = "/signup"
_lm.profile_view = "/lm-profile"
_lm.change_view = "/change"

_app.config.update(
    SECRET_KEY=_set["SECRET_KEY"],
    FLASK_LOGINMANAGER=_lm,
)


@_lm.user_loader
def load_user(user_id):
    """로그인메니저 user_loader 설정"""
    from db.user import AppUser

    return AppUser.query.get(user_id)


# endregion


# 패키지의 global property 정의
login_view = lambda: _lm.login_view
signup_view = lambda: _lm.signup_view
profile_view = lambda: _lm.profile_view
change_view = lambda: _lm.change_view


# 하위 모듈 로딩
from . import signup
from . import login
from . import logout
from . import profile
from . import status
from . import change


from db.user import AppUser
from db.group import Group

@_app.context_processor
def set_context():
    """세션 컨텍스트에 추가할 dict을 리턴한다"""

    util.debug("set_context()")

    dic = AppUser.max_len()
    dic.update(Group.max_len())
    dic["data"] = {}

    return dic  # _ctx