"""위치 추가 화면"""

from ._common import *
from dash.dependencies import Input, Output, State


def buildLocationSection():
    """Location의 빈 목록 및 편집 섹션을 생성"""

    list = buildLabel_Dropdown(
        "Location",
        "location",
        None,
        [],
        None,
        "yard",
        [("clear", "clear")],
    )

    name = buildLabel_Input("Name", "location", "name", "", Location.max_name)
    desc = buildLabel_Input("Description", "location", "desc", "", Location.max_desc)
    button = buildButtonRow("Add New Location", "location", True)

    return html.Section(
        [html.Hr(), list, name, desc, button],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Input("admin-manage-location-button", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onNewClick(n, uid, name, desc):
    """<Add> 버튼 작업 및 farm 목록 업데이트"""

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
    Input("admin-manage-location-save", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-location", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onSaveClick(n, uid, fid, name, desc):
    """<Save> 버튼 작업 및 목록 업데이트"""

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
    """<Clear> 버튼 작업 - 위치 삭제, 연결되 센서/센서데이터가 있으면 삭제 안함"""

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
