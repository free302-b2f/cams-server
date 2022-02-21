"""카메라 이미지 뷰어"""

print(f"<{__name__}> loading...")

from time import time as ttime, localtime, sleep
import os

from ._imports import *
from dash import no_update
from dash_extensions.enrich import Trigger

from db import location, sensor, user


# SENSOR_ID = "B2F_CAMs_1000000000001"
_ircam_path = "/static/ircam"


def _getFileTime(filePath: str) -> str:
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


def _decodeJpeg(sensors, imgURIs):
    """imgURIs 목록의 파일들에 대하여 메타데이터를 추출하여 _imgInfos에 저장한다"""

    # sensors = fl.session.sensors
    paths = [os.path.join(app.server.root_path, *u.split("/")) for u in imgURIs]
    imgInfos = ["-none-" for s in sensors]

    for j in range(len(paths)):
        try:
            jpg = paths[j]
            with open(jpg, "rb") as f:
                buf = f.read()
            metaLen = int(buf[-4:].decode("utf-8"))
            meta = buf[-metaLen:]
            ts = meta[0:32].decode("utf-8")
            sn = meta[32:-4].decode("utf-8")
            info(_decodeJpeg, f"ts={ts}, sn={sn}")

            ts = datetime.fromisoformat(ts).astimezone()
            ts = ts.replace(microsecond=0)
            imgInfos[j] = f"{sn} @ {ts.isoformat()}"
        except:
            imgInfos[j] = f"{sensors[j].sn} @ {_getFileTime(paths[j])}"
            pass
    return imgInfos


def getImageInfos():
    """글로벌 변수 - 센서목록, IR이미지 경로 등 - 를 초기화 한다"""

    user = fli.current_user
    if not user:
        return [[], [], []]

    sns = user.group.sensors
    uris = [(f"{_ircam_path}/{sns[i]}.jpg") for i in range(len(sns))]
    infos = _decodeJpeg(sns, uris)

    # _imgs = [f"apps-camera-img-{i}" for i in range(len(_sensors))]
    # _outputs = [Output(f"apps-camera-img-{i}", "src") for i in range(len(_sensors))]

    return [sns, uris, infos]


# init()


def layout():
    """dash 레이아웃"""

    sensors, uris, infos = getImageInfos()

    if len(sensors) == 0:
        return html.Div(
            html.H3(f"No IR Cameras"),
            className="apps-camera-title",
        )

    def build_img_container(index: int):
        return html.Div(
            [
                html.Img(
                    # id=f"apps-camera-img-{index}",
                    id={"model": "apps-camera-img", "id": index},
                    className="apps-camera-img",
                    **{"data-ws_uri": uris[index]},
                    src=uris[index],
                ),
                html.Div(
                    html.H3(f"IR Camera: {sensors[index].name}"),
                    id="apps-camera-title-{index}",
                    className="apps-camera-title",
                ),
                html.Div(
                    [
                        html.Span(""),
                        html.Span(
                            infos[index],
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
            *[build_img_container(i) for i in range(len(sensors))],
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

    # return no_update

    # sec = datetime.now().second % 30
    sec = localtime().tm_sec % 30
    print(f"ircam checking: {sec=} @ {datetime.now().isoformat()}")

    if sec >= 5 and sec < 10:
        print(f"ircam reloading: {sec=} @ {datetime.now().isoformat()}")
        sensors, uris, infos = getImageInfos()
        return [f"{u}?{ttime()}" for u in uris], infos
    else:
        # return [no_update for u in _uris].extend([no_update for u in _uris])
        return no_update


addPage(layout, "IR-CAM", 30)
