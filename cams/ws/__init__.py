"""패키지 초기화
 + __all__ 정의
"""

# region ---- __all__ 정의 ----

__all__ = ["server", "camera", "pool", "uploader"]

# endregion


# region ---- imports ----

import sys
from types import FunctionType

import flask as fl
import flask_login as fli

import apps.utility as util

# endregion


# region ---- DB 초기화 ----

_set = util.loadSettings("app_settings.json")["Postgres"]


# endregion


# region ---- 모듈의 global property 정의 ----

mpb = util.ModulePropertyBuilder(sys.modules[__name__])
#mpb.addProp("db", lambda: _db)

# endregion

