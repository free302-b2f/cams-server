"""센서 추가 화면"""

from ._common import *
from dash.dependencies import Input, Output, State


def buildSensorSection():
    """Sensor의 빈 목록 및 편집 섹션을 생성"""

    list = buildLabel_Dropdown(
        "CAMs",
        "sensor",
        None,
        [],
        None,
        "sensors",
        [("clear", "clear")],
    )
    name = buildLabel_Input("Sensor Name", "sensor", "name", "", Sensor.max_name)
    sn = buildLabel_Input("Sensor SN", "sensor", "sn", "", Sensor.max_sn)
    locs = buildLabel_Dropdown(
        "Location",
        "sensor",
        "location",
        [],
        None,
        "",
    )
    button = buildButtonRow("Add New Sensor", "sensor", True)

    return html.Section(
        [html.Hr(), list, name, sn, locs, button],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-sensor-button", "n_clicks"),
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
    Input("admin-manage-sensor-save", "n_clicks"),
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
