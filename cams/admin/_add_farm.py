"""팜 추가 화면"""

from admin._imports import *
from admin._common import *
# import visdcc

_farmName = html.Label(
    [
        html.Span("Farm Name"),
        html.Span("_", className="material-icons-two-tone"),
        dcc.Input(
            id="admin-manage-farm-name",
            type="text",
            maxLength=Farm.max_name,
            required=True,
        ),
    ],
    className="admin-manage-label",
)


addFarmSection = html.Section(
    [
        html.Hr(),
        _farmName,
        buildButtonRow("Add Farm", "farm"),
        # visdcc.Run_js('admin-manage-farm-add-js'),
    ],
    className="admin-manage-add-section",
)


@app.callback(
    Output("admin-manage-farm", "options"),
    Output("admin-manage-farm", "value"),
    Input("admin-manage-button-farm", "n_clicks"),
    State("admin-manage-user", "value"),
    State("admin-manage-farm-name", "value"),
    prevent_initial_call=True,
)
def onButtonClick(n, uid, farmName):
    """<Add Fram> 버튼 클릭시 db작업 및 farm 목록 업데이트"""

    if not n:
        return no_update

    user = AppUser.query.get(uid)
    farm = Farm(name=farmName)
    user.farms.append(farm)

    dba = db.get_dba()
    dba.session.commit()

    # trigger user change
    return buildFarmOptions(uid, farm.id)
