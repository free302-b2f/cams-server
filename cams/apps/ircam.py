from apps.imports import *
from dash import no_update

from db import sensor, user, farm

from time import sleep
from time import time as ttime

# SENSOR_ID = "B2F_CAMs_1000000000001"
_ircam_path = "/static/ircam"
_sensors: List[sensor.Sensor] = []
_uris: List[str]
_imgs: List[str]


def layout():
    """dash 레이아웃"""

    global _sensors, _uris, _imgs

    _user = fli.current_user
    _farms = _user.farms
    _sensors = []
    for f in _farms:
        _sensors.extend(f.sensors)
    _uris = [(f"{_ircam_path}/{_sensors[i].sn}.jpg") for i in range(len(_sensors))]
    _imgs = [f"apps-camera-img-{i}" for i in range(len(_sensors))]
    
    def build_img_container(index: int):
        return html.Div(
            [
                html.Img(
                    id=f"apps-camera-img-{index}",
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
                            "-none-",
                            id=f"apps-camera-info-{index}",
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
        [ build_img_container(i) for i in range(len(_sensors)) ],
        id="apps-camera-container",
        n_clicks=0,
    )


add_page(layout, "IR-CAM")
