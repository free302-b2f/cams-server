"""사용자 정보 변경 화면"""

from ._imports import *
from ._common import *


def buildLevelOptions(defaultLevel=None):
    """UserSection level dropdown에 사용할 목록"""

    # -3=탈퇴(삭제예정), -2=잠금(로그인 불가), -1=게스트, 0=일반, +1=그룹관리자, +2=마스터
    dic = {2: "마스터계정", 1: "그룹관리자", 0: "일반사용자", -1: "게스트", -2: "잠금", -3: "탈퇴(삭제)"}
    levels = [0]

    user: AppUser = fli.current_user
    if user:
        if user.level >= 1:
            # 기타 - 관리 권한 없음
            levels.insert(0, 1)
            levels.extend([-1, -2, -3])
        if user.level >= 2:
            # 마스터 계정인 경우 - 모든 사용자 관리
            levels.insert(0, 2)        

    options = [{"label": dic[v], "value": v} for v in levels]

    default = defaultLevel if defaultLevel in levels else 0
    if defaultLevel:
        default = defaultLevel if defaultLevel in levels else 0
    else:
        default = 0

    return options, default


userSection = html.Section(
    [
        html.Hr(),
        buildInputLabel("Login ID", "user", "username", "", AppUser.max_username, True),
        buildInputLabel("Email", "user", "email", "", AppUser.max_email),
        buildInputLabel("Real Name", "user", "realname", "", AppUser.max_realname),
        # buildInputLabel("Level", "user", "level", "", 2),
        buildDropdownLabel("Level", "user", "level", *buildLevelOptions()),
        buildButtonRow("Update User", "user", False),
    ],
    className="admin-manage-edit-section",
)


# @app.callback(
#     Output("admin-manage-sensor", "options"),
#     Output("admin-manage-sensor", "value"),
#     Input("admin-manage-button-sensor", "n_clicks"),
#     State("admin-manage-location", "value"),
#     State("admin-manage-sensor-name", "value"),
#     State("admin-manage-sensor-sn", "value"),
#     prevent_initial_call=True,
# )
# def onNewClick(n, fid, name, sn, desc):
#     """<Add Sensor> 버튼 클릭시 db작업 및 sensor 목록 업데이트"""

#     if not n:
#         return no_update

#     farm = Farm.query.get(fid)
#     sensor = Sensor(name=name, sn=sn, desc=desc)
#     farm.sensors.append(sensor)

#     dba = db.get_dba()
#     try:
#         dba.session.commit()
#     except:
#         return no_update

#     # trigger user change
#     return buildSensorOptions(fid, sensor.id)


# @app.callback(
#     Output("admin-manage-sensor", "options"),
#     Output("admin-manage-sensor", "value"),
#     Input("admin-manage-save-sensor", "n_clicks"),
#     State("admin-manage-location", "value"),
#     State("admin-manage-sensor", "value"),
#     State("admin-manage-sensor-name", "value"),
#     State("admin-manage-sensor-sn", "value"),
#     prevent_initial_call=True,
# )
# def onSaveClick(n, fid, sid, name, sn, desc):
#     """<Save Fram> 버튼 클릭시 db작업 및 목록 업데이트"""

#     if not n:
#         return no_update

#     dba = db.get_dba()
#     try:
#         sensor = Sensor.query.get(fid)
#         sensor.name = name
#         sensor.sn = sn
#         sensor.desc = desc
#         dba.session.commit()
#     except:
#         return no_update

#     # trigger user change
#     return buildSensorOptions(fid, sid)


# # admin-manage-sensor-clear
# @app.callback(
#     Output("admin-manage-sensor", "options"),
#     Output("admin-manage-sensor", "value"),
#     Input("admin-manage-sensor-clear", "n_clicks"),
#     State("admin-manage-location", "value"),
#     State("admin-manage-sensor", "value"),
#     prevent_initial_call=True,
# )
# def onClearClick(n, fid, sid):
#     """<Clear> 버튼 작업 - 센서 삭제, 센서데이터가 있으면 삭제 안함"""

#     if not n:
#         return no_update

#     dba = db.get_dba()
#     try:
#         sensor = Sensor.query.get(sid)
#         dba.session.delete(sensor)
#         dba.session.commit()
#     except:
#         return no_update

#     return buildSensorOptions(fid)
