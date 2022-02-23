"""공통 함수 - dcc.Dropdown에 사용할 목록 생성"""

from ._imports import *


def _getSelected(list, options, default):
    """옵션 목록의 선택값을 찾아 리턴"""

    # find selected value
    if default in list:  # 선택값이 주어진 경우
        selected = default
    else:  # 옵션목록의 첫번째 또는 빈값
        selected = options[0]["value"] if len(options) > 0 else ""
    return selected


def buildGroupOptions(gidSelected=None):
    """현재 로그인 사용자에 따라 Group 목록 리턴"""

    user: AppUser = fli.current_user

    # -3=탈퇴(삭제예정), -2=잠금(로그인 불가), -1=게스트, 0=일반, +1=그룹관리자, +2=마스터

    if user == None or not user.is_authenticated:
        groups = []
    elif user.is_master():  # 마스터 계정인 경우 - 모든 그룹
        groups = Group.query.all()
    else:  # 기타 - 소속그룹
        groups = [user.group]

    options = [{"label": f"{g.id}: {g.name} - {g.desc}", "value": g.id} for g in groups]
    selected = _getSelected([g.id for g in groups], options, gidSelected)
    return options, selected


def buildUserOptions(gid, uidSelected=None):
    """주어진 그룹의 AppUser 목록 리턴"""

    user: AppUser = fli.current_user
    group: Group = Group.query.get(gid)

    if user.is_gadmin() or user.is_master():
        users = group.users
    else:
        users = [user]

    options = [
        {"label": f"{u.id}: {u.username} - {u.realname}", "value": u.id} for u in users
    ]
    selected = _getSelected([u.id for u in users], options, uidSelected)
    return options, selected


def buildLevelOptions(levelSelected=None):
    """AppUser level dropdown에 사용할 목록"""

    # # -3=탈퇴(삭제예정), -2=잠금(로그인 불가), -1=게스트, 0=일반, +1=그룹관리자, +2=마스터
    # dic = {2: "마스터계정", 1: "그룹관리자", 0: "일반사용자", -1: "게스트", -2: "잠금", -3: "탈퇴(삭제)"}
    # levels = [0]

    user: AppUser = fli.current_user
    if user.is_authenticated:
        levels = user.get_levels()
    else:
        return [], ""

    options = [{"label": levels[v], "value": v} for v in levels]
    selected = _getSelected(levels, options, levelSelected)
    return options, selected


def buildLocationOptions(gid, lidSelected=None):
    """Location dropdown에 사용할 목록"""

    locations = Group.query.get(gid).locations
    options = [{"label": f"{l.id}: {l.name}", "value": l.id} for l in locations]

    selected = _getSelected([l.id for l in locations], options, lidSelected)
    return options, selected


def buildSensorOptions(gid, sidSelected=None):
    """Sensor dropdown에 사용할 목록"""

    sensors = Group.query.get(gid).sensors
    options = [{"label": f"{s.id}: {s.name}", "value": s.id} for s in sensors]
    selected = _getSelected([s.id for s in sensors], options, sidSelected)
    return options, selected
