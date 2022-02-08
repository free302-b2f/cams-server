"""사용자 정보 변경 화면"""

from ._common import *
from dash.dependencies import Input, Output, State


def buildUserSection():
    """사용자 섹션 - 사용자 선택 및 조작"""

    return html.Section(
        [
            # html.Hr(),
            buildLabel_Dropdown("User", "user", None, *buildUserOptions(), "badge"),
            # buildLabel_Dropdown("Group", "user", "group", *buildGroupOptions()),
            buildLabel_Input(
                "Login ID", "user", "username", "", AppUser.max_username, True
            ),
            buildLabel_Input("Email", "user", "email", "", AppUser.max_email),
            buildLabel_Input("Real Name", "user", "realname", "", AppUser.max_realname),
            buildLabel_Dropdown("Level", "user", "level", *buildLevelOptions()),
            buildButtonRow("Update User", "user", False),
        ],
        className="admin-manage-edit-section",
    )

