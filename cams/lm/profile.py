"""로그인한 사용자의 프로파일 뷰 및 콜백"""

print(f"<{__name__}> loading...")

from lm._imports import *
import lm.logout

from db.user import AppUser
from db.farm import Farm
from db.sensor import Sensor

from app import app, addPage
from dash import no_update
from apps._imports import *

_userMaxLen = AppUser.max_len()


def _action_icon(name: str, id: int, add: bool):
    """편집,삭제 아이콘 생성"""

    list = html.Span(
        [
            html.Span(
                "edit",
                className="material-icons-outlined",
                id={"model": f"edit-{name}", "id": id},
                n_clicks=0,
                **{f"data-{name}_id": id},
            ),
            html.Span(
                "save",
                className="material-icons-outlined",
                id={"model": f"save-{name}", "id": id},
                n_clicks=0,
                **{f"data-{name}_id": id},
            ),
            html.Span(
                "delete",
                className="material-icons-outlined",
                id={"model": f"delete-{name}", "id": id},
                n_clicks=0,
                **{f"data-{name}_id": id},
            ),
        ]
    )
    if add:
        list.children.append(
            html.Span(
                "add_circle_outline",
                className="material-icons-outlined",
                id={"model": f"add-{name}", "id": id},
                n_clicks=0,
                **{f"data-{name}_id": id},
            ),
        )
    return list


def buildPersonalLabel(labelText, userName, colName):
    return html.Label(
        [
            html.Span(labelText),
            dcc.Input(
                id=f"lm-profile-personal-{colName}",
                type="text",
                value=userName,
                maxLength=_userMaxLen[f"max_{colName}"],
                required=True,
                readOnly=True,
            ),
            html.Span("", className="material-icons-outlined"),
        ]
    )


def buildFarmLabel(id: int, name: str) -> html.Label:
    return html.Label(
        [
            html.Span(f"Farm {id}"),
            dcc.Input(
                # id=f"lm-profile-farms-{id}",
                id={"model": "farm", "id": id},
                type="text",
                value=name,
                maxLength=Farm.max_name,
                required=True,
                readOnly=True,
            ),
            _action_icon("farm", id, True),
        ]
    )


def buildSensorLabel(id: int, name: str) -> html.Label:
    return html.Label(
        [
            html.Span(f"Sensor {id}"),
            dcc.Input(
                id=f"lm-profile-sensors-{id}",
                type="text",
                value=name,
                maxLength=Sensor.max_sn + 5,
                required=True,
                readOnly=True,
            ),
            _action_icon("sensor", id, False),
        ]
    )


def layout():

    user = fli.current_user
    farms = user.farms #cursor.fetchall()
    sensors = {}
    for f in farms:
        sensors.update({s.id: s for s in f.sensors})

    _header = html.Header(
        [
            html.H4(
                [
                    html.Span("manage_accounts", className="material-icons-two-tone"),
                    html.Span(user.realname, className="font-sc"),  # "User Account",
                ],
                className="flex-h",
            ),
        ],
        id="lm-profile-header",
    )
    _menu = html.Section(
        [
            dcc.Link(
                [
                    html.Span("Change"),
                    html.Span("password", className="material-icons-two-tone"),
                ],
                href="lm.change",
                className="flex-h mr1",
            ),
            *(lm.logout.layout),
        ],
        className="flex-h-right",
        id="lm-profile-menu",
    )

    _profile = html.Section(
        [
            html.H5(
                [
                    html.Span("badge", className="material-icons-two-tone"),
                    "Personal Profile",
                    html.Span("edit", className="material-icons-outlined"),
                    # html.Span("save", className="material-icons-outlined"),
                ],
                className="flex-h",
            ),
            buildPersonalLabel("Login ID", user.username, "username"),
            buildPersonalLabel("Email", user.email, "email"),
            buildPersonalLabel("Real Name", user.realname, "realname"),
        ],
        id="lm-profile-personal",
        className="flex-v",
    )

    _farms = html.Section(
        [
            html.H5(
                [
                    html.Span("yard", className="material-icons-two-tone"),
                    "Farm List",
                    html.Span(
                        "add_box",
                        className="material-icons-outlined",
                        # id="lm-profile-farms-add",
                        n_clicks=0,
                    ),
                ],
                className="flex-h",
            ),
            *[buildFarmLabel(f.id, f.name) for f in farms],
        ],
        id="lm-profile-farms",
        className="flex-v",
    )

    _sensors = html.Section(
        [
            html.H5(
                [
                    html.Span("sensors", className="material-icons-two-tone"),
                    "Sensor List",
                    html.Span("add_box", className="material-icons-outlined"),
                ],
                className="flex-h",
            ),
            *[buildSensorLabel(s, sensors[s].name) for s in sensors],
        ],
        id="lm-profile-sensors",
        className="flex-v",
    )

    _settings = html.Section(
        [
            html.H5(
                [
                    html.Span("settings", className="material-icons-two-tone"),
                    "Preference",
                ],
                className="flex-h",
            ),
            html.Pre(" - 사용자 설정 사항..."),
        ],
        id="lm-profile-preference",
        className="flex-v",
    )

    _security = html.Section(
        [
            html.H5(
                [
                    html.Span("security", className="material-icons-two-tone"),
                    "Activity Log",
                ],
                className="flex-h",
            ),
            html.Pre(" - 활동/보안 기록..."),
        ],
        id="lm-profile-security",
        className="flex-v",
    )

    return html.Div(
        [
            _header,
            _menu,
            _profile,
            _farms,
            _sensors,
            _settings,
            _security,
            dcc.Location(id="lm-profile-url", refresh=True),
            html.Div(id="lm-profile-status", className="text-danger", n_clicks=0),
        ],
        id="lm-profile-container",
        className="content-pad",
    )

# Farm : add 
# @app.callback(Input("lm-profile-farms-add", "n_clicks"))
def addFarm(n: int):
    """add new farm to current user"""

    # TODO: 나중에 활성화

    if not n:
        return no_update

    user = fli.current_user
    farm = Farm(name="--new farm--")
    user.farms.append(farm)
    
    dba = fl.g.dba
    local_object = dba.session.merge(farm)
    dba.session.add(local_object)
    dba.session.commit()

    return 0

# Farm : delete
# @app.callback(
#     Output({"model": "delete-farm", "id": MATCH}, "n_clicks"),  # 더미
#     Trigger({"model": "delete-farm", "id": MATCH}, "n_clicks"),  # 이벤트 발생
#     State({"model": "delete-farm", "id": MATCH}, "data-farm_id"),  # 이벤트 소스의 팜 아이디
# )
def deleteFarm(fid):

    if not cbc.triggered[0]["value"]:
        return no_update

    farm = Farm.query.get(fid)
    from db import _dba

    try:
        local_object = _dba.session.merge(farm)
        _dba.session.delete(local_object)
        _dba.session.commit()    
    except:
        pass

    return 1

# Farm : enter edit mode
# @app.callback(
#     Output({"model": "farm", "id": MATCH}, "readonly"),  # farm_name input
#     # Output({"model": "save-farm", "id": MATCH}, "n_clicks"),  # 더미
#     Trigger({"model": "edit-farm", "id": MATCH}, "n_clicks"),  # 이벤트 발생
#     State({"model": "edit-farm", "id": MATCH}, "data-farm_id"),  # 이벤트 소스의 팜 아이디
# )
def editFarm(fid: int):
    """변경된 Farm 이름을 DB에 저장한다"""

    if not cbc.triggered[0]["value"]:
        return no_update

    return False


# Farm : save
# @app.callback(
#     Output({"model": "save-farm", "id": MATCH}, "n_clicks"),  # 더미
#     Trigger({"model": "save-farm", "id": MATCH}, "n_clicks"),  # 이벤트 발생
#     State({"model": "save-farm", "id": MATCH}, "data-farm_id"),  # 이벤트 소스의 팜 아이디
#     State({"model": "farm", "id": MATCH}, "value"),  # farm_name input
# )
def saveFarm(fid, newName: str):
    """변경된 Farm 이름을 DB에 저장한다"""

    if not cbc.triggered[0]["value"]:
        return no_update

    farm = Farm.query.get(fid)
    farm.name = newName

    from db import _dba
    local_object = _dba.session.merge(farm)
    # db.session.update(local_object)
    _dba.session.commit()

    return 1


# page reload callback
_receive_func = """
function(n, n2) 
{ 
    if (n > 0) setTimeout(() => location.reload(), 300); 
    for(let i = 0; i < n2.length; i++)
    {
        if(n2[i] > 0)
        {
            setTimeout(() => location.reload(), 300); 
            break;
        }
    }
}"""
# app.clientside_callback(
#     _receive_func,
#     Input("lm-profile-farms-add", "n_clicks"),
#     Input({"model": "delete-farm", "id": ALL}, "n_clicks"),  # 이벤트 발생
# )


# 이 페이지를 메인 라우터에 등록한다.
# add_page(layout, "Log In")  # test
addPage(layout)  # test
