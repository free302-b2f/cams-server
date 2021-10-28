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

import utility as util

# endregion


# region ---- DB 초기화 ----

_set = util.loadAppSettings("Postgres")


# endregion
