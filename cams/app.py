"""
Dash 객체를 생성하고 app 관련 기본 기능들을 정의
 - 로깅 함수
 - 메뉴바 관리 함수
"""

# region ---- imports ----

from typing import Any, Dict
import sys, os, logging
from datetime import timedelta, datetime

from flask_caching import Cache
from dash import Dash

import dash_bootstrap_components as dbc  # sidebar component

import apps.utility as util
import lm

# endregion


print(f"[{datetime.now()}] [D] [{__name__}] loading...")


# region ---- Dash 초기화 ----

"""설정파일 로딩 및 Dash 객체 생성/초기화"""
ext_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",  # graph
    dbc.themes.BOOTSTRAP,  # sidebar
]
ext_js = [
    "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
]  # TeX

# , suppress_callback_exceptions=True)
app = Dash(__name__, url_base_pathname="/")
app.config["suppress_callback_exceptions"] = True
app.config["external_stylesheets"] = ext_css
app.config["external_scripts"] = ext_js
server = app.server

os.chdir(server.root_path)
_set = util.loadSettings("app_settings.json")

_logging = _set["logging"]
app.logger.setLevel(_logging["Level"])
app.enable_dev_tools(dev_tools_ui=_logging["DevUi"], dev_tools_hot_reload=True)

cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "redis",  # 'filesystem',
        "CACHE_DIR": "cache_dir",
        "CACHE_REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6379"),
    },
)

# endregion


# region ---- Login Manager ----
"""LoginManager 생성 및 app 설정"""

# Login manager object will be used to login / logout users
login_manager = lm.get_manager(server)

# endregion


# region ---- configuration API ----
"""다른 모듈에서 설정 내용을 가져가는 API"""


def getConfigSection(section: str) -> Dict[str, Any]:
    """설정파일에서 주어진 섹션을 딕셔너리로 리턴한다"""

    return _set[section]


def getConfigValue(section: str, key: str) -> Any:
    """설정파일에서 주어진 섹션의 주어진 키의 값을 구한다"""

    return _set[section][key]


# endregion


# region ---- logging ----

from functools import singledispatch
from types import FunctionType


def log(level: str, caller: str, method: FunctionType, msg: Any):
    """메시지를 dash.app.logger를 이용해 기록한다"""

    message = f"[{datetime.now()}] [{level}] [{caller}]"
    if method != None:
        message += f" [{method.__name__}()]"
    message += f" {msg}"

    if level == "E":
        app.logger.error(message)
    elif level == "D":
        app.logger.debug(message)
    elif level == "I":
        app.logger.info(message)


@singledispatch
def error(method: FunctionType, msg):
    log("E", util.caller_module(3), method, msg)


@error.register(str)
def _(msg):
    log("E", util.caller_module(3), None, msg)


@singledispatch
def debug(method: FunctionType, msg):
    log("D", util.caller_module(3), method, msg)


@debug.register
def _(msg: str):
    log("D", util.caller_module(3), None, msg)


@singledispatch
def info(method: FunctionType, msg):
    log("I", util.caller_module(3), method, msg)


@info.register(str)
def _(msg):
    log("I", util.caller_module(3), None, msg)


# endregion


# region ---- APIs to register sub apps ----

router = {}  # map routing path into page layout
sidebar_items = {}  # map order into (menu title, page path)


def add_page(layout, menuName: str = None, menuOrder: int = 0):
    """페이지(dash app)의 이름과 레이아웃, 메뉴바에서의 순서를 저장한다.

    :param layout: 등록할 레이아웃
    :param menuName: 메뉴바에 표시할 텍스트
    :param menuOrder: 순서값, 낮을 수록 먼저 나온다."""

    pathName = f'{app.config["url_base_pathname"]}{util.caller_module()}'

    # display order in sidebar list
    if menuOrder == 0:
        menuOrder = len(router) * 10 + 1000

    # null name -> redirect url
    if menuName is None:
        debug(add_page, "menuName == None")
        return
    else:
        # check duplicated menuName
        name_count = len(
            list(filter(lambda x: x[0] == menuName, sidebar_items.values()))
        )
        if name_count > 0:
            menuName = menuName + f"#{name_count + 1}"

    # log
    debug(add_page, f"Adding: {menuOrder}, {menuName}, {pathName}")

    # add to dict
    router[pathName] = layout  # add layout
    sidebar_items[menuOrder] = (menuName, pathName)  # add sidebar item


# endregion
