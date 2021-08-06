# -*- coding: utf-8 -*-

#region ---- imports ----

import  sys, os, logging
from datetime import timedelta, datetime

from flask_caching import Cache
from dash import Dash

# sidebar component
import dash_bootstrap_components as dbc

#endregion

print(f'[{datetime.now()}] [D] [{__name__}] loading...')

ext_css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css', # graph
    dbc.themes.BOOTSTRAP, # sidebar
]
ext_js = ['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML']#TeX

app = Dash(__name__, url_base_pathname='/')#, suppress_callback_exceptions=True)
app.config['suppress_callback_exceptions'] = True
app.config['external_stylesheets'] = ext_css
app.config['external_scripts'] = ext_js
app.logger.setLevel(logging.DEBUG)
app.enable_dev_tools(dev_tools_ui=True, dev_tools_hot_reload=True)

server = app.server

cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis', # 'filesystem',
    'CACHE_DIR': 'cache_dir',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
})


  