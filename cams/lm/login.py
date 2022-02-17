"""로그인 뷰"""

print(f"<{__name__}> loading...")

import json
import lm
from lm._imports import *
from db.user import AppUser

# from app import app, debug


@fl.current_app.route("/login", methods=["GET", "POST"])
def login():
    """login 처리 결과를 json 문자열로 리턴"""

    nextPath = lm.profile_view()
    if fli.current_user.is_authenticated:
        return fl.redirect(nextPath)
    if fl.request.method == "GET":
        return fl.render_template("login.html")

    un = fl.request.form["lm-login-username"]
    pw = fl.request.form["lm-login-password"]

    response = {"isOK": False, "cause": "", "next": nextPath}
    user = AppUser.query.filter_by(username=un).first()

    if not user:
        response["cause"] = "lm-login-username"
    else:
        if user.level <= -2:
            response["cause"] = f"account <{un}> is locked or deleted"

        elif util.check_password_hash(user.password, pw):
            fli.login_user(user)

            response["isOK"] = True
            response["next"] = nextPath
        else:
            response["cause"] = "lm-login-password"

    return json.dumps(response)
