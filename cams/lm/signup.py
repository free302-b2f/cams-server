"""사인업 뷰"""

print(f"<{__name__}> loading...")

from lm._imports import *
# from db import get_dba #db sql alchemy
from db.user import AppUser
from app import app, debug
import json


# _ctx = AppUser.max_len()


@app.server.route("/signup", methods=["GET", "POST"])
def signup():

    if fl.request.method == "GET":
        return fl.render_template("signup.html")

    un = fl.request.form["lm-login-username"].strip()
    pw = fl.request.form["lm-login-password"].strip()
    pwc = fl.request.form["lm-login-password-confirm"].strip()
    em = fl.request.form["lm-login-email"].strip()
    rn = fl.request.form["lm-login-realname"].strip()

    response = {"isOK": False, "cause": "", "next": "/"}

    if not pw == pwc : 
        response["cause"] = "lm-login-password-confirm"
        return json.dumps(response)

    user = AppUser.query.filter_by(username=un).first()
    if user:
        response["cause"] = "lm-login-username"
    else:
        user = AppUser.query.filter_by(email=em).first()
        if user:
            response["cause"] = "lm-login-email"
        else:
            try:
                dba = fl.g.dba
                pwHash = wsec.generate_password_hash(pw, method="sha256")
                newUser = AppUser(username=un, password=pwHash, email=em, realname=rn)
                dba.session.add(newUser)
                dba.session.commit()
                response["isOK"] = True
            except:
                response["cause"] = "unknown"
    return json.dumps(response)


@app.server.context_processor
def set_login_context():
    """세션 컨텍스트에 추가할 dict을 리턴한다"""

    print(f"lm.signup.set_login_context(): entering...")

    return AppUser.max_len() #_ctx
