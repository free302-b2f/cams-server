from lm.imports import *
import db.user as db  # import User, getUserByName
from app import app

@app.server.route('/login', methods=['GET', 'POST'])
def test_login():

    if fl.request.method == "GET":
        return fl.render_template("login.html")
    
    username = fl.request.form["lm-login-username"]
    password = fl.request.form["lm-login-password"]

    user = db.firstBy(filterBy={"username": username})
    if user:
        if wsec.check_password_hash(user.password, password):
            fli.login_user(user)
            fl.flash('Logged in successfully.')       
            return fl.redirect(fl.url_for('/'))
    return "no user"


@app.server.context_processor
def set_login_context():

    ctx = dict()
    ctx["username_max"] = db.User.max_username
    ctx["password_max"] = db.User.max_password

    return ctx