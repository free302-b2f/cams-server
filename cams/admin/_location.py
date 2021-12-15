"""팜 추가 화면"""

from ._imports import *
from ._common import *
import flask as fl
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State

# import visdcc

_name = html.Label(
    [
        html.Span("Farm Name"),
        html.Span("_", className="material-icons-two-tone"),
        dcc.Input(
            id="admin-manage-location-name",
            type="text",
            maxLength=Location.max_name,
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
            id="admin-manage-location-desc",
            type="text",
            maxLength=Sensor.max_desc,
            required=True,
        ),
    ],
    className="admin-manage-label",
)


locationSection = html.Section(
    [
        html.Hr(),
        _name,
        _desc,
        buildButtonRow("Add New Farm", "farm"),
        # visdcc.Run_js('admin-manage-farm-add-js'),
    ],
    className="admin-manage-add-section",
)


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-button-farm", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onNewClick(n, uid, name, desc):
    """<Add New Fram> 버튼 클릭시 db작업 및 farm 목록 업데이트"""

    if not n:
        return no_update

    user = AppUser.query.get(uid)
    farm = Location(name=name)
    user.farms.append(farm)

    dba = fl.g.dba
    try:
        dba.session.commit()
    except:
        return no_update

    # trigger user change
    return buildLocationOptions(uid, farm.id)


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-save-farm", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-location", "value"),
    State("admin-manage-location-name", "value"),
    prevent_initial_call=True,
)
def onSaveClick(n, uid, fid, farmName):
    """<Save Fram> 버튼 클릭시 db작업 및 목록 업데이트"""

    if not n:
        return no_update

    dba = fl.g.dba
    try:
        farm = Location.query.get(fid)
        farm.name = farmName
        dba.session.commit()
    except:
        return no_update

    # trigger user change
    return buildLocationOptions(uid, fid)


# admin-manage-sensor-clear
@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-location-clear", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-location", "value"),
    prevent_initial_call=True,
)
def onClearClick(n, uid, fid):
    """<Clear> 버튼 작업 - 팜 삭제, 소유 센서가 있으면 삭제 안함"""

    if not n:
        return no_update

    dba = fl.g.dba
    try:
        farm = Location.query.get(fid)
        dba.session.delete(farm)
        dba.session.commit()
    except:
        return no_update

    return buildLocationOptions(uid)
