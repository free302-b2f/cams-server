"""패키지 admin 에서 공통으로 사용하는 함수"""

from ._common_options import *


def buildButtonRow(buttonText, modelName, showUpdateIcon: bool = False):
    """추가 항목에 사용할 버튼 생성
    + HTML IDs:
      - admin-manage-save-{modelName}   : save icon
      - admin-manage-button-{modelName} : add new button
      - data-model="{modelName}"        : button data-* property
    """

    icon = html.Span(
        "save",
        className="material-icons-outlined",
        id=f"admin-manage-save-{modelName}",
        n_clicks=0,
    )

    return html.Div(
        [
            html.Span("_", className="material-icons-two-tone"),
            html.Span("_", className="material-icons-two-tone"),
            html.Button(
                [
                    html.Span(
                        "add_circle_outline", className="material-icons-outlined"
                    ),
                    html.Span(buttonText, className="font-sc"),
                ],
                id=f"admin-manage-button-{modelName}",
                n_clicks=0,
                **{f"data-model": modelName},
            ),
            icon if showUpdateIcon else "",
        ],
        className="admin-manage-label",
    )


def buildLabel_Input(
    labelText, modelName, colName, value, maxLen, readonly: bool = False, addId=False
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


def buildLabel_Dropdown(
    labelText, modelName, colName, options, defaultValue, preIcon=None, postIcons=None
):
    """dcc.Dropdown을 포함한 html.Label 생성"""

    children = [
        html.Span(labelText),
        html.Span(preIcon if preIcon else "_", className="material-icons-two-tone"),
        dcc.Dropdown(
            id=f"admin-manage-{modelName}-{colName}"
            if colName
            else f"admin-manage-{modelName}",
            options=options,
            value=defaultValue,
            # required=True,
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

    return html.Label(
        children,
        className="admin-manage-label",
        id=f"admin-manage-{modelName}-{colName}-label"
        if colName
        else f"admin-manage-{modelName}-label",
    )
