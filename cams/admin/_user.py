"""사용자 정보 변경 화면"""

from ._common import *
from dash.dependencies import Input, Output, State


def buildUserSection():
    """AppUser의 빈 목록 및 편집 섹션 생성"""

    user: AppUser = fli.current_user
    isMaster = user.is_master()
    readOnly = not user.is_master() and not user.is_gadmin()
    
    list = buildLabel_Dropdown(
        "이용자 관리",
        "user",
        None,
        # *buildUserOptions(),
        [],
        None,
        "badge",
        [("clear", "clear")],
    )

    return html.Section(
        [
            html.Hr(),
            list,
            # buildLabel_Dropdown("Group", "user", "group", *buildGroupOptions()),
            buildLabel_Dropdown("Group", "user", "group", [], None),
            buildLabel_Input(
                "Login ID", "user", "username", "", AppUser.max_username, True
            ),
            buildLabel_Input("Email", "user", "email", "", AppUser.max_email),
            buildLabel_Input("Real Name", "user", "realname", "", AppUser.max_realname),
            buildLabel_Dropdown("Level", "user", "level", [], None),
            buildButtonRow("user", False),
        ],
        className="admin-manage-edit-section",
    )
