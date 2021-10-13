"""팜 추가 화면"""

from dash_html_components.Hr import Hr
from dash_html_components.Section import Section
from db.user import AppUser
from db.farm import Farm
from db.sensor import Sensor
import db

from app import app, add_page
from dash import no_update
from dash_extensions.enrich import Trigger
from apps.imports import *


# _set = getConfigSection("Postgres")
# _pgc = pg.connect(
#     f'postgres://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
# )

_users: List[AppUser] = AppUser.query.all()
_farms: List[Farm] = None
_sensors: List[Sensor] = None


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")

    # 센서 ID 추출
    global _users, _farms, _sensors
    # _farms = fli.current_user.farms
    # _sensors = {}
    # for f in _farms:
    #     _sensors.update({s.id: s for s in f.sensors})

    userOptions = [{"label": s.username, "value": s.id} for s in _users]
    userDefalut = userOptions[0]["value"] if len(userOptions) > 0 else ""

    headerRow = html.H4(
        [
            html.Span("yard", className="material-icons-two-tone"),
            html.Span("Manage Farm & Sensor", className="font-sc"),
        ],
        className="flex-h",
    )

    userRow = html.Label(
        [
            html.Span("User"),
            html.Span("badge", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="admin-farm-user",
                options=userOptions,
                value=userDefalut,
                clearable=False,
                searchable=False,
            ),
        ],
        className="admin-farm-label",
    )

    # _farms = _users[0].farms
    # farmOptions = [{"label": f.name, "value": f.id} for f in _farms]
    # farmDefalut = farmOptions[0]["value"] if len(farmOptions) > 0 else ""
    farmRow = html.Label(
        [
            html.Span("Farm"),
            html.Span("yard", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="admin-farm-farm",
                # options=farmOptions,
                # value=farmDefalut,
                clearable=False,
                searchable=False,
            ),
            html.Span(
                "add_box",
                className="material-icons-outlined",
                id="admin-farm-farm-add",
                n_clicks=0,
            ),
        ],
        className="admin-farm-label",
    )

    # _sensors={}
    # for f in _farms:
    #     _sensors.update({s.id: s for s in f.sensors})
    # sensorOptions = [{"label": _sensors[sid].name, "value": sid} for sid in _sensors]
    # sensorDefalut = sensorOptions[0]["value"] if len(sensorOptions) > 0 else ""
    sensorRow = html.Label(
        [
            html.Span("CAMs"),
            html.Span("sensors", className="material-icons-two-tone"),
            dcc.Dropdown(
                id="admin-farm-sensor",
                # options=sensorOptions,
                # value=sensorDefalut,
                clearable=False,
                searchable=False,
            ),
            html.Span(
                "add_box",
                className="material-icons-outlined",
                id="admin-farm-sensor-add",
                n_clicks=0,
            ),
        ],
        className="admin-farm-label",
    )

    buttonRow = html.Div(
        [
            html.Span("_", className="material-icons-two-tone"),
            html.Span("_", className="material-icons-two-tone"),
            html.Button(
                [
                    html.Span(
                        "add_circle_outline", className="material-icons-outlined"
                    ),
                    html.Span("Add New Farm", className="font-sc"),
                ],
                id="admin-farm-button",
                n_clicks=0,
                **{f"data-model": ""},
            ),
        ],
        className="admin-farm-label",
    )

    addFarmRow = html.Label(
        [
            html.Span("Farm Name"),
            html.Span("_", className="material-icons-two-tone"),
            dcc.Input(
                # id=f"lm-profile-farms-{id}",
                id="admin-farm-add-farm-name",
                type="text",
                maxLength=Farm.max_name,
                required=True,
            ),
        ],
        className="admin-farm-label",
    )

    return html.Div(
        [
            html.Header(headerRow, id="admin-farm-header"),
            html.Section(userRow),
            html.Section(farmRow),
            html.Section(sensorRow),
            html.Hr(),
            html.Section(
                [addFarmRow, buttonRow], id="admin-farm-add-section", className="hidden"
            ),
        ],
        id="admin-farm-container",
    )


@app.callback(
    Output("admin-farm-farm", "options"),
    Output("admin-farm-farm", "value"),
    Input("admin-farm-user", "value"),
)
def onUser(uid):

    if not uid:
        return no_update

    user = AppUser.query.get(uid)
    farms = user.farms
    farmOptions = [{"label": f.name, "value": f.id} for f in farms]
    farmDefalut = farmOptions[0]["value"] if len(farmOptions) > 0 else ""

    return farmOptions, farmDefalut


@app.callback(
    Output("admin-farm-sensor", "options"),
    Output("admin-farm-sensor", "value"),
    Input("admin-farm-farm", "value"),
)
def onFarm(fid):

    if not fid:
        return no_update

    farm = Farm.query.get(fid)
    sensors = farm.sensors
    sensorOptions = [{"label": s.name, "value": s.id} for s in sensors]
    sensorDefalut = sensorOptions[0]["value"] if len(sensorOptions) > 0 else ""

    return sensorOptions, sensorDefalut


@app.callback(
    Output("admin-farm-add-section", "className"),
    Output("admin-farm-button", "data-model"),
    Input("admin-farm-farm-add", "n_clicks"),
    prevent_initial_call=True,
)
def onFarmAddClick(n):

    if not n:
        return no_update
    
    return "", "farm"

@app.callback(
    Output("admin-farm-farm", "options"),
    Output("admin-farm-farm", "value"),
    Output("admin-farm-add-section", "className"),
    Input("admin-farm-button", "n_clicks"),
    State("admin-farm-user", "value"),
    State("admin-farm-button", "data-model"),
    prevent_initial_call=True,
)
def onButtonClick(n, uid):

    if not n:
        return no_update

    # user = AppUser.query.get(uid)
    # farm = Farm(name="KIST Pheno Farm")
    # farm.sensors.append(Sensor(sn="B2F_CAMs_1000000000001", name="Lab Sensor 1"))
    # user.farms.append(farm)

    # dba = db.get_dba()
    # dba.session.add(user)
    # dba.session.commit()

    # onFarm(farm.id)

    return no_update, no_update, "hidden"


add_page(layout, "Add-Farm")
