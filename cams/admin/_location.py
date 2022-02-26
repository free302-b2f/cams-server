"""위치 추가 화면"""

from ._common import *
from dash.dependencies import Input, Output, State
from db import sensor_data as sd


def buildLocationSection():
    """Location의 빈 목록 및 편집 섹션을 생성"""

    # calc permissions
    user: AppUser = fli.current_user
    isMaster, isGAdmin, isNormal, _ = user.is_levels()
    canAdd = isMaster or isGAdmin or isNormal
    canUpdate = isMaster or isGAdmin or isNormal
    canDelete = isMaster or isGAdmin

    list = buildLabel_Dropdown(
        "위치 관리",
        "location",
        None,
        [],
        None,
        "yard",
        [("clear", "delete")] if canDelete else None,
    )

    return html.Section(
        [
            list,
            buildLabel_Input(
                "Name", "location", "name", "", Location.max_name, not canUpdate
            ),
            buildLabel_Input(
                "Description", "location", "desc", "", Location.max_desc, not canUpdate
            ),
            buildButtonRow("location", canAdd, not canUpdate),
            buildStatusRow("location"),
        ],
        className="admin-manage-edit-section",
    )


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Output({"admin-manage-status-label": "location"}, "data"),
    Input("admin-manage-location-add", "n_clicks"),
    State("admin-manage-group", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onAddClick(n, gid, name, desc):
    """<Add> 버튼 작업 및 위치 목록 업데이트"""

    if not n:
        return no_update

    try:
        model: Location = Location(name=name, desc=desc, group_id=gid)
        db = fl.g.dba.session
        db.add(model)
        db.commit()
        return *buildLocationOptions(gid, model.id), [f"{model} 추가완료", cnOk]
    except Exception as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Output({"admin-manage-status-label": "location"}, "data"),
    Input("admin-manage-location-save", "n_clicks"),
    State("admin-manage-group", "value"),
    State("admin-manage-location", "value"),
    State("admin-manage-location-name", "value"),
    State("admin-manage-location-desc", "value"),
    prevent_initial_call=True,
)
def onUpdateClick(n, gid, id, name, desc):
    """<Update> 버튼 작업 및 목록 업데이트"""

    if not n:
        return no_update

    try:
        model: Location = Location.query.get(id)
        if model == None:
            raise AdminError("삭제됨 - 존재하지 않는 레코드")

        model.name = name
        model.desc = desc
        fl.g.dba.session.commit()
        return *buildLocationOptions(gid, id), ["업데이트 완료", cnOk]

    except AdminError as ex:
        return *buildLocationOptions(gid, id), [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-confirm", "trigger"),
    Output("admin-manage-confirm", "message"),
    Output({"admin-manage-status-label": "location"}, "data"),
    Input("admin-manage-location-delete", "n_clicks"),
    State("admin-manage-location", "value"),
    prevent_initial_call=True,
)
def onDeleteClick(n, id):
    """<Delete> 버튼 확인 대화상자"""

    if not n or not id:
        return no_update

    try:
        model: Location = Location.query.get(id)
        if model == None:
            raise AdminError("삭제됨 - 존재하지 않는 레코드")

        # 스토리지 위치는 삭제 불가
        if model.id == model.group.storage_id:
            raise AdminError("보관소 위치는 삭제할 수 없습니다")

        numRows = sd.Count(location_id=id)
        msg = f"위치를 삭제하면 위치에 연관된 센서데이터 <{numRows}>개도 모두 삭제됩니다."
        msg = f"{msg}\n\n위치 {model}를 삭제할까요?"
        return "location", msg, no_update

    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]


@app.callback(
    Output("admin-manage-location", "options"),
    Output("admin-manage-location", "value"),
    Output({"admin-manage-status-label": "location"}, "data"),
    Input("admin-manage-confirm", "submit_n_clicks"),
    State("admin-manage-confirm", "trigger"),
    State("admin-manage-location", "value"),
    prevent_initial_call=True,
)
def onDeleteConfirmed(n, src, id):
    """<Delete> 버튼 작업 - 위치 삭제, 연결되 센서/센서데이터가 있으면 삭제 안함"""

    if not n or src != "location":
        return no_update

    try:
        model: Location = Location.query.get(id)
        if model == None:
            raise AdminError("삭제됨 - 존재하지 않는 레코드")
        
        # 센서를 현재 위치에서 보관소로 이동
        db = fl.g.dba.session
        for s in model.sensors:
            s.location_id = model.group.storage_id
        db.commit()  # db.flush()

        # 데이터 삭제
        user: AppUser = fli.current_user
        if user.is_master() or user.is_gadmin():
            sd.f1_clear_data_location(model.id)

        db.delete(model)
        db.commit()
        return *buildLocationOptions(model.group_id), [f"{model} 삭제 완료", cnOk]

    except AdminError as ex:
        return no_update, no_update, [f"에러: {ex}", cnError]
    except:
        return no_update, no_update, [f"unknown error", cnError]
