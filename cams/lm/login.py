from lm.imports import *
from db.user import AppUser

from app import app, debug
import json

_ctx = AppUser.max_len()


@app.server.route("/login", methods=["GET", "POST"])
def login():

    if fl.request.method == "GET":
        return fl.render_template("login.html")

    un = fl.request.form["lm-login-username"]
    pw = fl.request.form["lm-login-password"]

    response = {"isOK": False, "cause": "", "next": "/"}

    # user = User.firstBy(filterBy={"username": un})
    user = AppUser.query.filter_by(username=un).first()
    

    if not user:
        response["cause"] = "lm-login-username"
    else:
        if user.level <= -2:
            response["cause"] = f"account <{un}> is locked"

        elif wsec.check_password_hash(user.password, pw):
            fli.login_user(user)
            
            response["isOK"] = True
            response["next"] = "/lm-profile"
        else:
            response["cause"] = "lm-login-password"

    return json.dumps(response)


@app.server.context_processor
def set_login_context():

    return _ctx
