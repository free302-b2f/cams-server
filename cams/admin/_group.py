"""그룹 관리 화면"""

from ._common import *
from dash.dependencies import Input, Output, State


def buildGroupSection():
    _list = buildLabel_Dropdown(
        "Group", "group", None, *buildGroupOptions(), "groups"
    )
    _name = buildLabel_Input("Group Name", "group", "name", "", Group.max_name)
    _desc = buildLabel_Input("Sensor SN", "group", "desc", "", Group.max_desc)
    _button = buildButtonRow("Add New Group", "group", True)
    return html.Section(
        [html.Hr(), _list, _name, _desc, _button],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-button-sensor", "n_clicks"),
    State("admin-manage-location", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    prevent_initial_call=True,
)
def onNewClick(n, fid, name, sn):
    """<Add> 버튼 작업 및 sensor 목록 업데이트"""

    if not n:
        return no_update

    loc = Location.query.get(fid)
    sensor = Sensor(name=name, sn=sn)
    loc.sensors.append(sensor)

    dba = fl.g.dba
    try:
        dba.session.commit()
    except:
        return no_update

    # trigger user change
    return buildSensorOptions(fid, sensor.id)


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-save-sensor", "n_clicks"),
    State("admin-manage-location", "value"),
    State("admin-manage-sensor", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    prevent_initial_call=True,
)
def onSaveClick(n, fid, sid, name, sn):
    """<Save> 버튼 작업 및 목록 업데이트"""

    if not n:
        return no_update

    dba = fl.g.dba
    try:
        sensor = Sensor.query.get(fid)
        sensor.name = name
        sensor.sn = sn
        dba.session.commit()
    except:
        return no_update

    # trigger user change
    return buildSensorOptions(fid, sid)


# admin-manage-sensor-clear
@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-sensor-clear", "n_clicks"),
    State("admin-manage-location", "value"),
    State("admin-manage-sensor", "value"),
    prevent_initial_call=True,
)
def onClearClick(n, fid, sid):
    """<Clear> 버튼 작업 - 센서 삭제, 센서데이터가 있으면 삭제 안함"""

    if not n:
        return no_update

    dba = fl.g.dba
    try:
        sensor = Sensor.query.get(sid)
        dba.session.delete(sensor)
        dba.session.commit()
    except:
        return no_update

    return buildSensorOptions(fid)
