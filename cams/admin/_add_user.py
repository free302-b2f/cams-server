"""사용자 정보 변경 화면"""

from ._imports import *
from ._common import *

addUserSection = html.Section(
    [
        html.Hr(),
        buildInputLabel("Login ID", "user", "username", "", AppUser.max_username, True),
        buildInputLabel("Email", "user", "email", "", AppUser.max_email),
        buildInputLabel("Real Name", "user", "realname", "", AppUser.max_realname),
        buildButtonRow("Update User", "user", False),
    ],
    className="admin-manage-add-section",
)


# @app.callback(
#     Output("admin-manage-sensor", "options"),
#     Output("admin-manage-sensor", "value"),
#     Input("admin-manage-button-sensor", "n_clicks"),
#     State("admin-manage-farm", "value"),
#     State("admin-manage-sensor-name", "value"),
#     State("admin-manage-sensor-sn", "value"),
#     State("admin-manage-sensor-desc", "value"),
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
#     State("admin-manage-farm", "value"),
#     State("admin-manage-sensor", "value"),
#     State("admin-manage-sensor-name", "value"),
#     State("admin-manage-sensor-sn", "value"),
#     State("admin-manage-sensor-desc", "value"),
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
#     State("admin-manage-farm", "value"),
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
