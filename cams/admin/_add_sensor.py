"""센서 추가 화면"""

from ._imports import *
from ._common import *
from dash.dependencies import Input, Output, State
import flask_login as fl

_name = html.Label(
    [
        html.Span("Sensor Name"),
        html.Span("_", className="material-icons-two-tone"),
        dcc.Input(
            id="admin-manage-sensor-name",
            type="text",
            maxLength=Sensor.max_name,
            required=True,
        ),
    ],
    className="admin-manage-label",
)

_sn = html.Label(
    [
        html.Span("Sensor SN"),
        html.Span("_", className="material-icons-two-tone"),
        dcc.Input(
            id="admin-manage-sensor-sn",
            type="text",
            maxLength=Sensor.max_sn,
            required=True,
        ),
    ],
    className="admin-manage-label",
)

_desc = html.Label(
    [
        html.Span("Description"),
        html.Span("_", className="material-icons-two-tone"),
        dcc.Input(
            id="admin-manage-sensor-desc",
            type="text",
            maxLength=Sensor.max_desc,
            required=True,
        ),
    ],
    className="admin-manage-label",
)

addSensorSection = html.Section(
    [
        html.Hr(),
        _name,
        _sn,
        _desc,
        buildButtonRow("Add New Sensor", "sensor"),
    ],
    className="admin-manage-add-section",
)


@app.callback(
    Output("admin-manage-sensor", "options"),
    Output("admin-manage-sensor", "value"),
    Input("admin-manage-button-sensor", "n_clicks"),
    State("admin-manage-farm", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    State("admin-manage-sensor-desc", "value"),
    prevent_initial_call=True,
)
def onNewClick(n, fid, name, sn, desc):
    """<Add Sensor> 버튼 클릭시 db작업 및 sensor 목록 업데이트"""

    if not n:
        return no_update

    farm = Farm.query.get(fid)
    sensor = Sensor(name=name, sn=sn, desc=desc)
    farm.sensors.append(sensor)

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
    State("admin-manage-farm", "value"),
    State("admin-manage-sensor", "value"),
    State("admin-manage-sensor-name", "value"),
    State("admin-manage-sensor-sn", "value"),
    State("admin-manage-sensor-desc", "value"),
    prevent_initial_call=True,
)
def onSaveClick(n, fid, sid, name, sn, desc):
    """<Save Fram> 버튼 클릭시 db작업 및 목록 업데이트"""

    if not n:
        return no_update

    dba = fl.g.dba
    try:
        sensor = Sensor.query.get(fid)
        sensor.name = name
        sensor.sn = sn
        sensor.desc = desc
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
    State("admin-manage-farm", "value"),
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
