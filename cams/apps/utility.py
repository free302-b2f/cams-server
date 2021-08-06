# -*- coding: utf-8 -*-

#region ---- imports ----
from datetime import timedelta, datetime, timezone
from os import path
from typing import Tuple
import random, sys

from dash import callback_context as cbc
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import flask
#endregion
 
def caller_module(level=2):
    '''Get calling module name'''
    f = sys._getframe(level)
    return f.f_globals['__name__']
