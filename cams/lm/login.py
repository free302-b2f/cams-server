from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app

_ctx = dict()


@app.server.route("/login", methods=["GET", "POST"])
def test_login():

    global _ctx

    if fl.request.method == "GET":
        _ctx.update(
            {
                "ph_un": "login id",
                "ph_pw": "password",
            }
        )
        return fl.render_template("login.html")

    un = fl.request.form["lm-login-username"]
    pw = fl.request.form["lm-login-password"]
    _ctx.update({"ph_un": un, "ph_pw": pw})

    user = db.firstBy(filterBy={"username": un})
    if user:
        if wsec.check_password_hash(user.password, pw):
            fli.login_user(user)
            fl.flash("Logged in successfully.")
            return fl.redirect(fl.url_for("/"))
    return "no user"


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
