"""센서 추가 화면"""

from admin._imports import *
from admin._common import *


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
        buildButtonRow("Add Sensor", "sensor"),
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
def onButtonClick(n, fid, name, sn, desc):
    """<Add Sensor> 버튼 클릭시 db작업 및 sensor 목록 업데이트"""

    if not n:
        return no_update

    farm = Farm.query.get(fid)
    sensor = Sensor(name=name, sn=sn, desc=desc)
    farm.sensors.append(sensor)

    dba = db.get_dba()
    try:
        dba.session.commit()
    except: 
        return no_update

    # trigger user change
    return buildSensorOptions(fid, sensor.id)


