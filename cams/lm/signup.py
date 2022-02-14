"""사인업 뷰"""

print(f"<{__name__}> loading...")

from lm._imports import *
from db.user import AppUser
from db.group import Group
from app import app, debug
import json


# _ctx = AppUser.max_len()


@app.server.route("/signup", methods=["GET", "POST"])
def signup():

    if fl.request.method == "GET":
        # group list
        groups = Group.query.filter(Group.name != "GUEST")
        dic = [g.to_dict() for g in groups]
        return fl.render_template("signup.html", groups=dic)

    un = fl.request.form["lm-login-username"].strip()
    pw = fl.request.form["lm-login-password"].strip()
    pwc = fl.request.form["lm-login-password-confirm"].strip()
    em = fl.request.form["lm-login-email"].strip()
    rn = fl.request.form["lm-login-realname"].strip()
    gn = fl.request.form["lm-login-group"].strip()

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
                # pwHash = wsec.generate_password_hash(pw, method="sha256")
                pwHash = util.generate_password_hash(pw)
                newUser = AppUser(username=un, password=pwHash, email=em, realname=rn)
                group = Group.query.filter_by(name=gn)
                if group == None:
                    response["cause"] = "lm-login-group"
                    return json.dumps(response)
                newUser.group = group[0]
                dba.session.add(newUser)
                dba.session.commit()
                response["isOK"] = True
            except:
                response["cause"] = "unknown"
    return json.dumps(response)


@app.server.context_processor
def set_context():
    """세션 컨텍스트에 추가할 dict을 리턴한다"""

    debug("set_context()")



    return AppUser.max_len() #_ctx
