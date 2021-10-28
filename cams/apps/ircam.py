from datetime import timedelta, datetime, timezone, time, date
from time import time as ttime, localtime, sleep
import os

from ._imports import *
import flask_login as fli
from dash import no_update
import dash_html_components as html
import dash_core_components as dcc
from dash_extensions.enrich import Trigger
from dash.dependencies import Input, Output, State, MATCH, ALL

from db import sensor, user, farm


# SENSOR_ID = "B2F_CAMs_1000000000001"
_ircam_path = "/static/ircam"
_sensors = []
_uris = []
_imgs = []
_imgInfos = []
_outputs = []


def getFileTime(filePath: str):
    """주어진 경로의 OS 파일시스템에 저장된 수정시각을 리턴한다"""

    try:
        if os.path.isfile(filePath):
            ts = os.path.getmtime(filePath)
            ts = datetime.fromtimestamp(ts).astimezone()
            ts = ts.replace(microsecond=0)
            return ts.isoformat()
        else:
            return "-none-"
    except:
        return "-none-"


def decodeJpeg():
    """_uris 목록의 파일들에 대하여 메타데이터를 추출하여 _imgInfos에 저장한다"""

    global _imgInfos
    paths = [os.path.join(app.server.root_path, *u.split("/")) for u in _uris]
    _imgInfos = ["-none-" for s in _sensors]
    rng = range(len(paths))

    for j in range(len(paths)):
        try:
            jpg = paths[j]
            with open(jpg, "rb") as f:
                buf = f.read()
            metaLen = int(buf[-4:].decode("utf-8"))
            meta = buf[-metaLen:]
            ts = meta[0:32].decode("utf-8")
            sn = meta[32:-4].decode("utf-8")
            info(decodeJpeg, f"ts={ts}, sn={sn}")

            ts = datetime.fromisoformat(ts).astimezone()
            ts = ts.replace(microsecond=0)
            _imgInfos[j] = f"{sn} @ {ts.isoformat()}"
        except:
            _imgInfos[j] = f"{_sensors[j].sn} @ {getFileTime(paths[j])}"
            pass


def init():
    """글로벌 변수 - 센서목록, IR이미지 경로 등 - 를 초기화 한다"""

    global _sensors, _uris, _imgs, _outputs

    _user = fli.current_user
    if not _user:
        return

    _farms = _user.farms
    _sensors = []
    for f in _farms:
        _sensors.extend(f.sensors)
    _uris = [(f"{_ircam_path}/{_sensors[i].sn}.jpg") for i in range(len(_sensors))]
    _imgs = [f"apps-camera-img-{i}" for i in range(len(_sensors))]
    decodeJpeg()

    _outputs = [Output(f"apps-camera-img-{i}", "src") for i in range(len(_sensors))]


# init()


def layout():
    """dash 레이아웃"""

    init()

    def build_img_container(index: int):
        return html.Div(
            [
                html.Img(
                    # id=f"apps-camera-img-{index}",
                    id={"model": "apps-camera-img", "id": index},
                    className="apps-camera-img",
                    **{"data-ws_uri": _uris[index]},
                    src=_uris[index],
                ),
                html.Div(
                    html.H3(f"IR Camera: {_sensors[index].name}"),
                    id="apps-camera-title-{index}",
                    className="apps-camera-title",
                ),
                html.Div(
                    [
                        html.Span(""),
                        html.Span(
                            _imgInfos[index],
                            # id=f"apps-camera-info-{index}",
                            id={"model": "apps-camera-info", "id": index},
                            className="apps-camera-info",
                        ),
                    ],
                    id=f"apps-camera-info-box-{index}",
                    className="apps-camera-info-box",
                ),
            ],
            id=f"apps-camera-img-container-{index}",
            className="apps-camera-img-container",
        )

    return html.Div(
        [
            *[build_img_container(i) for i in range(len(_sensors))],
            dcc.Interval(
                id="apps-camera-interval",
                interval=5_000,  # in milliseconds
                n_intervals=0,
            ),
        ],
        id="apps-camera-container",
        n_clicks=0,
    )


@app.callback(
    Output({"model": "apps-camera-img", "id": ALL}, "src"),
    Output({"model": "apps-camera-info", "id": ALL}, "children"),
    Trigger("apps-camera-interval", "n_intervals"),
)
def pull():
    """pull new image"""

    # sec = datetime.now().second % 30
    sec = localtime().tm_sec % 30
    print(f"ircam checking: {sec=} @ {datetime.now().isoformat()}")

    if sec >= 5 and sec < 10:
        print(f"ircam reloading: {sec=} @ {datetime.now().isoformat()}")
        decodeJpeg()
        return [f"{u}?{ttime()}" for u in _uris], _imgInfos
    else:
        # return [no_update for u in _uris].extend([no_update for u in _uris])
        return no_update


addPage(layout, "IR-CAM", 30)
