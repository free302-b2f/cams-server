from sqlalchemy.sql.expression import false
from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app
import json


_ctx = dict()


@app.server.route("/signup", methods=["GET", "POST"])
def signup():

    global _ctx

    if fl.request.method == "GET":
        _ctx.update(
            {
                "ph_un": "login id",
                "ph_pw": "password",
                "ph_pwc": "password",
                "ph_em": "email address",
            }
        )
        return fl.render_template("signup.html")

    un = fl.request.form["lm-login-username"].strip()
    pw = fl.request.form["lm-login-password"].strip()
    pwc = fl.request.form["lm-login-password-confirm"].strip()
    em = fl.request.form["lm-login-email"].strip()
    _ctx.update({"ph_un": un, "ph_pw": pw, "ph_pwc": pwc, "ph_em": em})

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

    global _ctx

    _ctx.update(
        {
            "max_un": db.User.max_username,
            "max_pw": db.User.max_password,
            "max_em": db.User.max_email,
        }
    )
    return _ctx
