"""공통 함수 - dcc.Dropdown에 사용할 목록 생성"""

from ._imports import *


def buildUserOptions():
    """AppUser dropdown에 사용할 목록"""

    user: AppUser = fli.current_user

    if user == None:
        users = []
    elif user.level >= 2:
        # 마스터 계정인 경우 - 모든 사용자 관리
        users = AppUser.query.all()
    elif user.level == 1:
        # 그룹 관리자 계정 경우 - 소속 그룹 사용자 관리
        users = AppUser.query.filter_by(group_id=user.group_id)
    else:
        # 일반 계정 경우 - 로그인한 사용자 자신만 관리
        users = [user]
    options = [{"label": f"{u.username}({u.realname})", "value": u.id} for u in users]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, default


def buildLevelOptions(defaultLevel=None):
    """AppUser level dropdown에 사용할 목록"""

    # -3=탈퇴(삭제예정), -2=잠금(로그인 불가), -1=게스트, 0=일반, +1=그룹관리자, +2=마스터
    dic = {2: "마스터계정", 1: "그룹관리자", 0: "일반사용자", -1: "게스트", -2: "잠금", -3: "탈퇴(삭제)"}
    levels = [0]

    user: AppUser = fli.current_user
    if user:
        if user.level >= 1:
            # 기타 - 관리 권한 없음
            levels.insert(0, 1)
            levels.extend([-1, -2, -3])
        if user.level >= 2:
            # 마스터 계정인 경우 - 모든 사용자 관리
            levels.insert(0, 2)

    options = [{"label": dic[v], "value": v} for v in levels]

    default = defaultLevel if defaultLevel in levels else 0
    if defaultLevel:
        default = defaultLevel if defaultLevel in levels else 0
    else:
        default = 0

    return options, default


def buildGroupOptions(uid=None):
    """Group dropdown에 사용할 목록"""

    user: AppUser = fli.current_user

    # -3=탈퇴(삭제예정), -2=잠금(로그인 불가), -1=게스트, 0=일반, +1=그룹관리자, +2=마스터

    if user == None:
        groups = []
    elif user.level >= 2:
        # 마스터 계정인 경우 - 모든 그룹
        groups = Group.query.all()
    elif user.level == 1:
        # 그룹관리자 - 소속그룹
        g1 = AppUser.query.get(uid).group if uid else user.group
        groups = [g1]
    elif user.level == 1 or user.level == 0:
        # 그룹 소속된 경우 - 소속그룹
        g1 = AppUser.query.get(uid).group if uid else user.group
        groups = [g1]
    else:
        groups = []
    options = [{"label": f"{g.name}({g.desc})", "value": g.id} for g in groups]
    default = options[0]["value"] if len(options) > 0 else ""
    g1 = AppUser.query.get(uid).group if uid else user.group
    return options, g1.id if uid else default


def buildLocationOptions(uid, selected=None):
    """Location dropdown에 사용할 목록"""

    user = AppUser.query.get(uid)
    locations = user.group.locations
    options = [{"label": f.name, "value": f.id} for f in locations]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, selected if selected else default


def buildSensorOptions(uid, selected=None):
    """Sensor dropdown에 사용할 목록"""

    user = AppUser.query.get(uid)
    sensors = user.group.sensors
    options = [{"label": s.name, "value": s.id} for s in sensors]
    default = options[0]["value"] if len(options) > 0 else ""
    return options, selected if selected else default
