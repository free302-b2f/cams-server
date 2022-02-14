"""
+ WebApp 공통 - DO NOT import any WebApp module

- Dash 객체를 생성하고
- 라우팅/메뉴바 관리 함수 정의
"""

print(f"<{__name__}> loading...")

# region ---- imports ----

# from typing import Any, Dict
import sys, os, threading
from datetime import date, datetime, time, timedelta, timezone

from flask_caching import Cache
from dash import Dash
from dash_extensions.enrich import (
    DashProxy,
    Trigger,
    TriggerTransform,
    MultiplexerTransform,
    # ServersideOutputTransform,
    NoOutputTransform,
)

import dash_bootstrap_components as dbc  # sidebar component

#!TODO: app.py에서는 utility이외의 모듈을 임포트하면 안됨 ~ 크로스 레퍼런스 에러
from utility import error, debug, info, loadAppSettings, getCallerModule

# endregion


# region ---- Dash 초기화 ----

# 설정파일 로딩 및 Dash 객체 생성/초기화
ext_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",  # graph
    dbc.themes.BOOTSTRAP,  # sidebar
]

# app = Dash(__name__, url_base_pathname="/")
app = DashProxy(
    __name__,
    url_base_pathname="/",
    transforms=[NoOutputTransform(), TriggerTransform(), MultiplexerTransform()],
)
app.config["suppress_callback_exceptions"] = True
app.config["prevent_initial_callbacks"] = False
app.config["external_stylesheets"] = ext_css
# app.config["external_scripts"] = ext_js

# Ubunut에서 os.chdir(server.root_path) 필요
os.chdir(app.server.root_path)
_set = loadAppSettings()
app.config.update(APP_SETTINGS=_set)
app.server.config.update(APP_SETTINGS=_set)

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


# region ---- configuration API ----
"""다른 모듈에서 설정 내용을 가져가는 API"""


def getSettings(section: str, key:str = None):
    """설정파일에서 주어진 섹션을 딕셔너리로 리턴한다"""

    return _set[section][key] if key else _set[section]


# endregion


# region ---- APIs to register sub apps ----

router = {}  # map routing path into page layout
sidebar_items = {}  # map order into (menu title, page path)


def addPage(layout, menuName: str = None, menuOrder: int = 0, addPath: str = None):
    """페이지(dash app)의 이름과 레이아웃, 메뉴바에서의 순서를 저장한다.

    :param layout: 등록할 레이아웃
    :param menuName: 메뉴바에 표시할 텍스트
    :param menuOrder: 순서값, 낮을 수록 먼저 나온다."""

    moduleName = getCallerModule().replace(".", "-")
    pathName = f'{app.config["url_base_pathname"]}{moduleName}'

    # display order in sidebar list
    if menuOrder == 0:
        menuOrder = len(router) * 10 + 1000

    # check duplicated menuName
    if menuName:
        name_count = len(
            list(filter(lambda x: x[0] == menuName, sidebar_items.values()))
        )
        if name_count > 0:
            menuName = menuName + f"#{name_count + 1}"

    # log
    debug(addPage, f"Adding: {menuOrder}, {menuName}, {pathName}")

    # add to dict
    router[pathName] = layout  # add layout
    if addPath:
        if addPath in router:
            raise KeyError(f"route path '{addPath}' is registered already")
        router[addPath] = layout  # additional path

    if menuName:
        sidebar_items[menuOrder] = (menuName, pathName, moduleName)  # add sidebar item


# endregion
