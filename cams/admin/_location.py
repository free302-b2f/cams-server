"""팜 추가 화면"""

# from ._imports import *
from ._common import *
# import flask as fl
# from dash import html
# from dash import dcc
from dash.dependencies import Input, Output, State

# import visdcc

_name = html.Label(
    [
        html.Span("Location Name"),
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
        buildButtonRow("Add New Location", "location"),
        # visdcc.Run_js('admin-manage-farm-add-js'),
    ],
    className="admin-manage-edit-section",
)


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-button-location", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onNewClick(n, uid, name, desc):
    """<Add New Location> 버튼 클릭시 db작업 및 farm 목록 업데이트"""

    if not n:
        return no_update

    group: Group = AppUser.query.get(uid).group
    location = Location(name=name, desc=desc)
    group.locations.append(location)

    try:
        fl.g.dba.session.commit()
    except:
        return no_update

    # trigger user change
    return buildLocationOptions(uid, location.id)


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-save-location", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-location", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onSaveClick(n, uid, fid, name, desc):
    """<Save Fram> 버튼 클릭시 db작업 및 목록 업데이트"""

    if not n:
        return no_update

    try:
        farm = Location.query.get(fid)
        farm.name = name
        farm.desc = desc
        fl.g.dba.session.commit()
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
    """<Clear> 버튼 작업 - 팜 삭제, 연결되 센서/센서데이터가 있으면 삭제 안함"""

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
