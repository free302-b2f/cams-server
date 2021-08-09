'''
CAMs 센서데이터의 시각화
'''

#region ---- import ----

from datetime import datetime, timezone, date, timedelta
from timeit import default_timer as timer
from typing import List, Tuple

import pandas as pd, numpy as np
import matplotlib.pyplot as plt

from bson.raw_bson import RawBSONDocument
from pymongo import MongoClient, has_c as pm_has_c
from pymongo.cursor import Cursor

import psycopg2 as pg
import psycopg2.extensions as pge
import psycopg2.extras as pga

from flask import request

from dash import callback_context as cbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import plotly.express as px
import plotly.graph_objects as go

from app import app, cache, add_page, router, error, debug, info, getConfigSection
import apps.utility as util

#endregion

debug('loading...')

#region ---- DB Server & Connection ----

_cams = getConfigSection('Cams')#CAMs 설정

if _cams['DbmsKey'] == 'Mongo':
    _setDb = getConfigSection('Mongo')#CAMs DB 설정
    _mongoClient = MongoClient(
        f'mongodb://{_setDb["User"]}:{_setDb["Pw"]}@{_setDb["Ip"]}:{_setDb["Port"]}/{_setDb["Db"]}', 
        document_class=RawBSONDocument)
    _camsDb = _mongoClient[_setDb["Db"]]
    
else:
    _setDb = getConfigSection('Postgres')
    _connPg = pg.connect(f'postgres://{_setDb["User"]}:{_setDb["Pw"]}@{_setDb["Ip"]}:{_setDb["Port"]}/{_setDb["Db"]}')

#endregion

def load_data(farmName, sn, date) -> Tuple[List[float], pd.DataFrame, List[str]]:
    '''DB에서 하루동안의 데이터를 불러온다.
    쿼리 시간과 DataFrame 변환시간의 리스트를 생성
    테이블의 필드이름 목록을 생성    
    :return: 소요시간과 DataFrame, 필드이름 목록의 튜플'''

    def query_mongo() -> Tuple[Cursor, List[str]]:
        sensors = _camsDb['sensors']
        ds = sensors.find({'SN':sn,'Date':date})
        cols = _setDb['DataColumns']
        # data_types = {x:'float64' for x in cols}
        # meta_columns = _setDb['MetaColumns']
        # for x in meta_columns: data_types[x] = 'string'
        return (ds, cols)

    def query_postgres(sn, cols, ds) -> Tuple[List, List[str]]:
        cursor:pge.cursor = _connPg.cursor()
        start = datetime(2021, 2,16) #datetime.now().strftime('%Y-%m-%d')
        end = start + timedelta(hours=23, minutes=59, seconds=59, microseconds=999999)
        sql = cursor.mogrify("""SELECT * FROM sensor_data 
            WHERE (sensor_id = (SELECT id FROM sensord WHERE sn = %s)) 
            AND (time BETWEEN %s AND %s)
            ORDER BY time DESC LIMIT 10000""", (sn, start, end))
        cursor.execute(sql)   
        cols = [x.name for x in cursor.description]     
        ds = cursor.fetchall()
        cursor.close()
        return ds, cols

    timing=[0,0]
    startTime = timer()
    ds, cols = query_mongo() if _cams['DbmsKey'] == 'Mongo' else query_postgres()
    timing[0] = round(timer() - startTime, 3)

    startTime = timer()
    df = pd.DataFrame(ds)#.astype(data_types)
    timing[1] = round(timer() - startTime, 3)

    debug(load_data, f'{date}: {df.shape = }')

    return (timing, df, cols)
#load_data("", "B2F_CAMs_1000000000001", "20210117")#test

def plot(df:pd.DataFrame, cols:List[str] = [], title:str = "B2F CAMs") -> dict:
    '''데이터의 Figure 생성'''

    if(df is None or len(df) == 0): 
        return px.scatter(pd.DataFrame({x:[0] for x in cols}), y=cols, title=title)

    df.sort_values(by=['Time'], axis=0, inplace=True)
    return {
        'data':[go.Scatter(
            x=df['Time'], 
            y=df[i], 
            mode='lines', 
            name=i
            ) for i in cols],
        'layout':go.Layout(
            title = title,
            xaxis_title = 'Time',
            yaxis_title = 'Data',
            #legend ={'itemwidth':30}
            )
    }
#plot(query_sensors("", "B2F_CAMs_1000000000001", "20210117"), 'test plot') #test


@app.callback(
    [Output('graph1', 'figure'), Output('log-listing', 'children')],
    [Input('SN', 'value'), Input('Date', 'date'), Input('sampling-ratio', 'value')])
def update_graph(SN, date, sampleRatio):#Year, Month, Day):    
    '''선택된 정보로 그래프를 업데이트 한다'''

    debug(update_graph, f'{SN = }, {date = }, {sampleRatio = }')

    #date == None
    if date is None: 
        listing = util.formatTiming(request, 
            [_setDb["Name"], _setDb["Ip"], _setDb["Port"]], [0,0,0], 0)
        return [plot(None), listing]

    dbSN = f'B2F_CAMs_100000000000{SN}'
    dbDate = datetime.fromisoformat(date).strftime('%Y%m%d')

    timing, df, cols = load_data('B2F', dbSN, dbDate)

    cbc.record_timing('Query', timing[0], 'query DB')
    cbc.record_timing('DataFrame', timing[0], 'pandas DataFrame')
    startTime = timer()

    frac=(float(sampleRatio) if(sampleRatio is not None) else 100)/100.0
    if(frac < 1): df = df.sample(frac=frac)
    fig = plot(df, cols, f'{dbSN} : {dbDate}')

    timing.append(round(timer() - startTime, 3))
    cbc.record_timing('DataTable', timing[2], 'dash view')

    listing = util.formatTiming(request, [_setDb["Name"], _setDb["Ip"], _setDb["Port"]], timing, df.shape)

    return [fig, listing]

@app.callback(Output('cams-sr-label', 'children'), Input('sampling-ratio', 'value'))
def update_time(sampleRatio):
    '''샘플링 비율에 따른 샘플간격을 업데이트 한다'''

    frac=(float(sampleRatio) if(sampleRatio!=None) else 0)/100.0
    return f'{0.5 / frac} minutes'

def layout():
    '''Dash의 layout을 설정한다'''

    debug(layout, f'entering...')
    app.title = 'B2F - CAMs Viewer'

    def tr(label:str, el, elId:str=None, merge:bool=False):
        '''주어진 내용을 html TR에 출력한다'''

        if merge :
            tr = html.Tr(html.Td(el, style={'width':'100%', 'padding':'2px 5px'}, 
            colSpan='10', className='cams_table_td'))        
        else:
            tr = html.Tr([
            html.Td(html.Label(label, htmlFor=elId if(elId!=None) else label), 
                    style={'width':'15%', 'padding':'2px 5px'}, className='cams_table_td'),
            html.Td(el, style={'width':'40%', 'padding':'2px 5px'}, className='cams_table_td'),
            html.Td('', style={'width':'100%','padding':'2px 5px'}, className='cams_table_td'),
            ])
        return tr
    
    dateValue=date(2021, 2, 16)#datetime.now().date()
    snOptions = [{'label': f'Sensor {x}', 'value': x} for x in range(1,4)]

    return html.Div([
        html.H3('B2F CAMs Viewer'), html.Hr(),
        html.Listing('', id='log-listing', className='log-listing'),

        html.Table([
        
        tr('','',merge=True),    

        tr('Sensor', dcc.Dropdown(id='SN', options=snOptions, value=snOptions[0]['value']), 'SN'),

        tr('Date', dcc.DatePickerSingle(id='Date', display_format='YYYY-MM-DD', date=date(2021, 2, 16))),

        tr('Sample Ratio(%)', 
           [dcc.Input(id='sampling-ratio', value='100', type='number', min=0, max=100, step=1,debounce=True),
            html.Span('100%', id='cams-sr-label')], 
           'sampling-ratio'),
        
        tr('Graph', dcc.Graph(id='graph1', className='camsGraphBorder'), merge=True)

        ], className='cams_contents_table'),#~table
    ])
#layout()#test

#이 페이지를 메인 메뉴바에 등록한다.
add_page(layout, "CAMs", 40)
