from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app, debug
import json


_ctx = db.User.max_len()


@app.server.route("/signup", methods=["GET", "POST"])
def signup():

    if fl.request.method == "GET":
        return fl.render_template("signup.html")

    un = fl.request.form["lm-login-username"].strip()
    pw = fl.request.form["lm-login-password"].strip()
    pwc = fl.request.form["lm-login-password-confirm"].strip()
    em = fl.request.form["lm-login-email"].strip()

    response = {"isOK": False, "cause": "", "next": "/"}

    user = db.firstBy(filterBy={"username": un})
    if user:
        response["cause"] = "lm-login-username"
    else:
        user = db.firstBy(filterBy={"email": em})
        if user:
            response["cause"] = "lm-login-email"
        else:
            try:
                db.insert(username=un, password=pw, email=em)
                response["result"] = True
            except:
                response["cause"] = "unknown"
    return json.dumps(response)


@app.server.context_processor
def set_login_context():

    return _ctx
