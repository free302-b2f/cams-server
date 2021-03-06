"""패키지 apps 에서 공통으로 사용하는 외부모듈 임포트 목록"""

# from types import FunctionType, LambdaType, ModuleType
# from typing import Any, Callable, Tuple, List, Dict
from datetime import date, datetime, time, timedelta, timezone
# import random, sys
# from os import path, getcwd
# from timeit import default_timer as timer
# import pandas as pd, numpy as np

#mongo db
# from bson.raw_bson import RawBSONDocument
# from pymongo import MongoClient, has_c as pm_has_c
# from pymongo.cursor import Cursor

#postgresql db
# import psycopg2 as pg
# import psycopg2.extensions as pge
# import psycopg2.extras as pga

#flask
import flask as fl
import flask_login as fli
# import werkzeug.security as wsec
# from flask import request

#dash
from dash import no_update
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash import html
from dash import dcc

#plotly
# import plotly.express as px
# import plotly.graph_objects as go

#app & apps
from app import app, router, addPage, getSettings
from utility import error, debug, info #, loadAppSettings, getCallerModule, parseDate
