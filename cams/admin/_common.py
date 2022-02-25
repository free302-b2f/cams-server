"""패키지 admin 에서 공통으로 사용하는 함수"""

from ._common_options import *


def buildButtonRow(modelName, showAddIcon=False, hidden=False):
    """html.Div 생성 - Button과 Icon을 포함
    + HTML IDs:
      - admin-manage-{modelName}-save   : save icon
      - admin-manage-{modelName}-add    : add new button
      - data-model="{modelName}"        : button data-* property
    """

    addIcon = (
        html.Span(
            "add_circle_outline",
            className="material-icons-outlined",
            id=f"admin-manage-{modelName}-add",
            n_clicks=0,
        )
        if showAddIcon
        else None
    )

    hiddenStyle = {"display": "none"} if hidden else {}

    return html.Div(
        [
            html.Span("_", className="material-icons-two-tone"),
            html.Span("_", className="material-icons-two-tone"),
            html.Button(
                [
                    html.Span("save", className="material-icons-outlined"),
                    html.Span(f"Update {modelName.capitalize()}", className="font-sc"),
                ],
                id=f"admin-manage-{modelName}-save",
                n_clicks=0,
                **{f"data-model": modelName},
            ),
            addIcon,
        ],
        className="admin-manage-label",
        style=hiddenStyle,
    )


def buildLabel_Input(
    labelText, modelName, colName, value, maxLen, readonly: bool = False
):
    """dcc.Input을 포함한 html.Label 생성"""

    return html.Label(
        [
            html.Span(labelText),
            html.Span("_", className="material-icons-two-tone"),
            dcc.Input(
                id=f"admin-manage-{modelName}-{colName}",
                type="text",
                value=value,
                maxLength=maxLen,
                required=True,
                readOnly=readonly,
            ),
        ],
        className="admin-manage-label",
        id=f"admin-manage-{modelName}-{colName}-label",
    )


def buildLabel_Check(labelText, modelName, colName, value, readonly: bool = False):
    """dcc.Input checkbox type을 포함한 html.Label 생성"""

    return html.Label(
        [
            html.Span(labelText),
            html.Span("_", className="material-icons-two-tone"),
            dcc.Checklist(
                options=[
                    {
                        "value": True,
                        "label": " 소유하지 않음 - 데이터 수신하지 않음",
                        "disabled": readonly,
                    }
                ],
                value=[],
                id=f"admin-manage-{modelName}-{colName}",
                inline=True,
            ),
        ],
        className="admin-manage-label",
        id=f"admin-manage-{modelName}-{colName}-label",
    )


def buildLabel_Dropdown(
    labelText,  # 라벨 텍스트
    modelName,  # ORM 테이블 클래스 이름
    colName,  # ORM 컬럼 이름
    options,  # dcc.Dropdown에 사용할 모델 목록
    defaultValue,  # dcc.Dropdown의 선택값
    preIconText=None,  # dcc.Dropdown 앞에 올 아이콘
    postIcons=None,  # dcc.Dropdown 뒤에 올 아이콘의 (아이콘텍스트,아이디) 목록
    hidden=False,
):
    """dcc.Dropdown을 포함한 html.Label 생성"""

    children = [
        html.Span(labelText),
        html.Span(
            preIconText if preIconText else "_", className="material-icons-two-tone"
        ),
        dcc.Dropdown(
            id=f"admin-manage-{modelName}-{colName}"
            if colName
            else f"admin-manage-{modelName}",
            options=options,
            value=defaultValue,
            clearable=False,
            searchable=False,
        ),
    ]

    if postIcons:
        for icon in postIcons:
            children.append(
                html.Span(
                    icon[0],
                    className="material-icons-outlined",
                    id=f"admin-manage-{modelName}-{icon[1]}",
                    n_clicks=0,
                )
            )

    hiddenStyle = {"display": "none"} if hidden else {}
    return html.Label(
        children,
        className="admin-manage-label",
        id=f"admin-manage-{modelName}-{colName}-label"
        if colName
        else f"admin-manage-{modelName}-label",
        style=hiddenStyle,
    )
