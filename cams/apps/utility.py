"""
코드 중복 방지를 위한 자주 쓰는 함수 모음
"""

#region ---- imports ----
from typing import Any, Tuple, List, Dict
from datetime import timedelta, datetime, timezone
from os import path
import random, sys, json

from dash import callback_context as cbc
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import flask
#endregion

_pyVersion = sys.version_info[:3]
 
def caller_module(level=2):
    '''호출하는 함수가 정의된 모듈의 이름을 구한다'''

    f = sys._getframe(level)
    return f.f_globals['__name__']


def parseDate(dateStr:str, timeStr:str=None) -> datetime:
    '''개별 문자열로 표현된 날짜와 시각을 `datetime`으로 파싱

    usage: parseDate('20210216', '12:34:56')
    '''
    if(timeStr == None): 
        return datetime.strptime(dateStr, '%Y%m%d')
    else: 
        return datetime.strptime(f'{dateStr}{timeStr}', '%Y%m%d%H:%M:%S')
#parseDate('20210216', '12:34:56')


def getHttpInfo(flaskRequest) -> Tuple:
    '''HTTP 서버와 클라이언트 정보를 튜플로 리턴한다
    
    :param flaskRequest: flask.request 객치
    :return : Tuple(host name, client ip, browser name, broser version)'''

    host = flaskRequest.headers.get("Host")
    client = flaskRequest.remote_addr
    browser = flaskRequest.user_agent.browser
    version = flaskRequest.user_agent.version
    return (host, client, browser, version)


def formatTiming(flaskRequest, dbServer:list, timing:list, dataSize) -> List[str]:
    '''주어진 정보를 서버정보와 함께 문자열 목록으로 리턴한다
    
    :param flaskRequest: flask.request
    :param dbServer: list[dbms name, db server ip, db server port]
    :param timing: 소요시간 list[
        db query & dataset 생성, 
        dataset -> pandas.DataFrame 변환, 
        DataFrame -> dash.Graph / dash.DataTable 변환]'''

    http = getHttpInfo(flaskRequest)
    pyVersion = sys.version_info[:3]
    return [
        f'Client: {http[2]} {http[3]} @ {http[1]}\n',
        f'Web Server: Python {pyVersion[0]}.{pyVersion[1]}.{pyVersion[2]} @ {http[0]}\n',
        f'DB Server: {dbServer[0]} @ {dbServer[1]}:{dbServer[2]}\n',
        f'Shape of records: {dataSize}\n',
        f'Timing(sec): Query={timing[0]}, pandas.DataFrame={timing[1]}, dash.view={timing[2]}\n'
    ]


def callback_triggered_by(ids:List[str]) -> bool:
    '''Dash callback함수가 주어진 아이디에 의해 호출된 것인지 검사한다

    :param ids: 체크할 HTML 요소의 ID 목록'''
    
    if not cbc.triggered: return False
    else:
        triggered_ids = [ x['prop_id'].split('.')[0] for x in cbc.triggered]
        for id in triggered_ids:
            if id in ids: return True
        return False


_Body = List[Tuple[dbc.Label, dbc.Input]]
_Footer = List[dbc.Button]
def showPopup(id, header:str, body:_Body, footer:_Footer) -> dbc.Modal:
    '''HTML 팝업창을 만든다.

    :param id: 팝업창의 DOM ID
    :param header: 헤더 부분의 텍스트
    :param body: 팝업창의 내용 - label과 input 쌍의 목록
    :param footer: 팝업창의 하단 버튼 목록
    :return dash_bootstrap_components.Modal'''

    return dbc.Modal(
    [
        dbc.ModalHeader(header),
        dbc.ModalBody(body),
        dbc.ModalFooter(footer),
    ], id=id, )


def loadSettings(section:str) -> Dict[str, Any]:
    '''설정파일을 읽어 dict를 리턴한다.

    :param: section: 설정파일에서 읽어올 섹션의 키
    :return: 주어진 섹션의 설정값의 dict
    '''

    fn = 'app_settings.json'
    with open(fn, 'r', encoding='utf-8') as fp:
        config = json.load(fp)[section]

    return config

#loadConfig('Mongo')

