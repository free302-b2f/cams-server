"""공통 함수 - dcc.Dropdown에 사용할 목록 생성"""

from ._imports import *


def buildGroupOptions(gid=None):
    """현재 로그인 사용자에 따라 Group 목록 리턴"""

    user: AppUser = fli.current_user

    # -3=탈퇴(삭제예정), -2=잠금(로그인 불가), -1=게스트, 0=일반, +1=그룹관리자, +2=마스터

    if user == None or not user.is_authenticated:
        groups = []
    elif user.is_master():  # 마스터 계정인 경우 - 모든 그룹
        groups = Group.query.all()
    else:  # 기타 - 소속그룹
        groups = [user.group]
    options = [
        {"label": f"{g.id} : {g.name} : {g.desc}", "value": g.id} for g in groups
    ]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, default if gid == None else gid


def buildUserOptions(gid):
    """주어진 그룹의 AppUser 목록 리턴"""

    group = Group.query.get(gid)
    options = [
        {"label": f"{u.id} : {u.username}: {u.realname}", "value": u.id}
        for u in group.users
    ]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, default


def buildLevelOptions(defaultLevel=None):
    """AppUser level dropdown에 사용할 목록"""

    # # -3=탈퇴(삭제예정), -2=잠금(로그인 불가), -1=게스트, 0=일반, +1=그룹관리자, +2=마스터
    # dic = {2: "마스터계정", 1: "그룹관리자", 0: "일반사용자", -1: "게스트", -2: "잠금", -3: "탈퇴(삭제)"}
    # levels = [0]

    user: AppUser = fli.current_user
    if user.is_authenticated:
        levels = user.get_levels()

    options = [{"label": levels[v], "value": v} for v in levels]

    default = defaultLevel if defaultLevel in levels else 0
    if defaultLevel:
        default = defaultLevel if defaultLevel in levels else 0
    else:
        default = 0

    return options, default


def buildLocationOptions(gid, selected=None):
    """Location dropdown에 사용할 목록"""

    group = Group.query.get(gid)
    locations = group.locations
    options = [{"label": f"{l.id} : {l.name}", "value": l.id} for l in locations]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, selected if selected else default


def buildSensorOptions(gid, selected=None):
    """Sensor dropdown에 사용할 목록"""

    group = Group.query.get(gid)
    sensors = group.sensors
    options = [{"label": f"{s.id} : {s.name}", "value": s.id} for s in sensors]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, selected if selected else default
