"""암호변경 뷰"""

print(f"<{__name__}> loading...")

import lm
from lm._imports import *
from db.user import AppUser
from db.group import Group

# from app import app, debug
import json


@fl.current_app.route("/change", methods=["GET", "POST"])
def change_pwd():
    """암호변경 결과를 json 문자열로 리턴"""

    # settings = fl.g.settings["Cams"]
    user = fli.current_user

    if not fli.current_user.is_authenticated:
        return fl.redirect(lm.login_view())
    if fl.request.method == "GET":
        dic = {
            "userIsReadOnly": True,
            "userValue": f"{user.username} ({user.realname})",
            # "userId": user.id,
        }
        return fl.render_template("change.html", data=dic)

    pw = fl.request.form["lm-login-password"].strip()
    pwn = fl.request.form["lm-login-password-new"].strip()
    pwc = fl.request.form["lm-login-password-confirm"].strip()

    response = {"isOK": False, "cause": "", "next": lm.profile_view()}

    if not pwn == pwc:
        response["cause"] = "lm-login-password-confirm"
    elif util.check_password_hash(user.password, pw):
        response["cause"] = "lm-login-password"
    else:
        try:
            dba = fl.g.dba

            user.password = util.generate_password_hash(pwn)
            dba.session.commit()
            response["isOK"] = True
        except:
            response["cause"] = "unknown"
    return json.dumps(response)
