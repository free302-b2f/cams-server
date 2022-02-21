"""사인업 뷰"""

print(f"<{__name__}> loading...")

from lm._imports import *
from db.user import AppUser
from db.group import Group
# from app import app, debug
import json


@fl.current_app.route("/signup", methods=["GET", "POST"])
def signup():
    """signup 결과를 json 문자열로 리턴"""

    settings = fl.g.settings["Cams"]

    if fl.request.method == "GET":
        # group list
        if not settings["IS_PRIVATE_SERVER"]:
            groups = [g.to_dict() for g in Group.query.all()]
        else:
            groups = None
        return fl.render_template("signup.html", groups=groups)#, data=dic)

    un = fl.request.form["lm-login-username"].strip()
    pw = fl.request.form["lm-login-password"].strip()
    pwc = fl.request.form["lm-login-password-confirm"].strip()
    em = fl.request.form["lm-login-email"].strip()
    rn = fl.request.form["lm-login-realname"].strip()

    response = {"isOK": False, "cause": "", "next": "/"}

    if not pw == pwc:
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

                # 새 사용자 생성
                newUser = AppUser(
                    username=un,
                    password=util.generate_password_hash(pw),
                    email=em,
                    realname=rn,
                )

                # group
                gid = (
                    settings["DB_PRIVATE_GROUP_ID"]
                    if settings["IS_PRIVATE_SERVER"]
                    else fl.request.form["lm-login-group"]
                )               
                newUser.group_id = gid

                # level
                group = Group.query.get(gid)
                if len(group.users) == 0:
                    newUser.level = AppUser.level_group_admin # 1st user == group admin

                dba.session.add(newUser)
                dba.session.commit()
                response["isOK"] = True
            except:
                response["cause"] = "unknown"
    return json.dumps(response)


# @app.server.context_processor
# def set_context():
#     """세션 컨텍스트에 추가할 dict을 리턴한다"""

#     debug("set_context()")

#     dic = AppUser.max_len()
#     dic.update(Group.max_len())
#     dic["data"] = {}

#     return dic  # _ctx
