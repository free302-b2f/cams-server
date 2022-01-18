"""
코드 중복 방지를 위한 자주 쓰는 함수 모음
"""

print(f"<{__name__}> loading...")

# region ---- imports ----

from types import FunctionType, LambdaType, ModuleType
from typing import Any, Callable, Tuple, List, Dict
from datetime import timedelta, datetime, timezone
from os import path, getcwd
import sys, json

# endregion


def addSuperDir(filepath):
    import sys, os.path as path

    # dir = path.dirname(path.dirname(__file__))
    dir = path.dirname(path.dirname(filepath))
    sys.path.insert(0, dir)


def getCallerModule(level=2) -> str:
    """호출하는 함수가 정의된 모듈의 이름을 구한다"""

    f = sys._getframe(level)
    return f.f_globals["__name__"]


def parseDate(dateStr: str, timeStr: str = None) -> datetime:
    """개별 문자열로 표현된 날짜와 시각을 `datetime`으로 파싱

    usage: parseDate('20210216', '12:34:56')
    """
    if timeStr == None:
        return datetime.strptime(dateStr, "%Y%m%d")
    else:
        return datetime.strptime(f"{dateStr}{timeStr}", "%Y%m%d%H:%M:%S")


# parseDate('20210216', '12:34:56')


def callback_triggered_by(ids: List[str]) -> bool:
    """Dash callback함수가 주어진 아이디에 의해 호출된 것인지 검사한다

    :param ids: 체크할 HTML 요소의 ID 목록"""

    from dash import callback_context as cbc

    if not cbc.triggered:
        return False
    else:
        triggered_ids = [x["prop_id"].split(".")[0] for x in cbc.triggered]
        for id in triggered_ids:
            if id in ids:
                return True
        return False


def buildPopup(id, header: str, body=[], footer=[]):
    """HTML 팝업창을 만든다.

    :param id: 팝업창의 DOM ID
    :param header: 헤더 부분의 텍스트
    :param body: 팝업창의 내용 - label과 input 쌍의 목록
    :param footer: 팝업창의 하단 버튼 목록
    :return dash_bootstrap_components.Modal"""

    import dash_bootstrap_components as dbc

    return dbc.Modal(
        [
            dbc.ModalHeader(header),
            dbc.ModalBody(body),
            dbc.ModalFooter(footer),
        ],
        id=id,
    )


_APP_SETTINGS_FILE = "app_settings.json"
# _APP_SETTINGS_FILE = "app_settings_b2f.json"


def loadAppSettings(section: str = None) -> Dict[str, Any]:
    """설정파일을 읽어 dict를 리턴한다.

    :return: 설정값의 dict
    """

    with open(_APP_SETTINGS_FILE, "r", encoding="utf-8") as fp:
        config = json.load(fp)

    return config[section] if section else config


# region ---- logging ----

from functools import singledispatch
from types import FunctionType
import flask as fl


def log(level: str, caller: str, method: FunctionType, msg: Any):
    """메시지를 dash.app.logger를 이용해 기록한다"""

    message = f"[{datetime.now()}] [{level}] [{caller}]"
    if method != None:
        message += f" [{method.__name__}()]"
    message += f" {msg}"

    try:
        app = fl.current_app._get_current_object()

        if level == "E":
            app.logger.error(message)
        elif level == "D":
            app.logger.debug(message)
        elif level == "I":
            app.logger.info(message)
    except:
        print(message)


@singledispatch
def error(method: FunctionType, msg):
    log("E", getCallerModule(3), method, msg)


@error.register(str)
def _(msg):
    log("E", getCallerModule(3), None, msg)


@singledispatch
def debug(method: FunctionType, msg):
    log("D", getCallerModule(3), method, msg)


@debug.register
def _(msg: str):
    log("D", getCallerModule(3), None, msg)


@singledispatch
def info(method: FunctionType, msg):
    log("I", getCallerModule(3), method, msg)


@info.register(str)
def _(msg):
    log("I", getCallerModule(3), None, msg)


# endregion


import werkzeug.security as wsec


def generate_password_hash(password: str) -> str:
    return wsec.generate_password_hash(password, method="pbkdf2:sha512", salt_length=32)


def check_password_hash(pwhash: str, password: str) -> bool:
    return wsec.check_password_hash(pwhash, password)
