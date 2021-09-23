from apps.imports import *
from dash import no_update
from dash_extensions import WebSocket

from ws.server import get_ws_info
from db import sensor, user, farm

from time import sleep
from time import time as ttime

SENSOR_ID = "B2F_CAMs_1000000000001"
_ws_url = get_ws_info(f"download")

_sensors: dict = {}
_sensorOptions: list = []

_random = random.Random()

def layout():

    global _sensors, _sensorOptions

    _user = fli.current_user
    _farms = _user.farms
    _sensors = {}
    for f in _farms:
        _sensors.update({s.id: s for s in f.sensors})
    _sensorOptions = [{"label": _sensors[id].name, "value": id} for id in _sensors]
    _sensorDefault = _sensorOptions[0]["value"] if len(_sensorOptions) else ""

    return html.Div(
        [
            html.Div(
                [
                    html.Img(id="apps-camera-img"),
                    html.Div(html.H3("IR Camera View"), id="apps-camera-title"),
                    html.Div(
                        [
                            html.Span(""),
                            html.Span("-none-", id="apps-camera-info"),
                        ],
                        id="apps-camera-info-box",
                    ),
                    WebSocket(id="apps-camera-ws", url=_ws_url),
                ],
                id="apps-camera-img-container",
            ),
            html.Div(
                [
                    html.Label(
                        [
                            html.Span("Sensor"),
                            dcc.Dropdown(
                                id="apps-camera-control-sensor",
                                options=_sensorOptions,
                                value=_sensorDefault,
                                clearable = False,
                            ),
                        ]
                    ),
                    html.Label(
                        [
                            html.Span("SN"),
                            dcc.Input(
                                id="apps-camera-control-sn",
                                type="text",
                                placeholder="--SN--",
                                readOnly=True,
                                debounce=True,
                            ),
                        ],
                    ),
                    html.Label(
                        [
                            html.Span("Location(Farm)"),
                            dcc.Input(
                                id="apps-camera-control-farm",
                                type="text",
                                placeholder="붉은 수수밭",
                                readOnly=True,
                                debounce=True,
                            ),
                        ],
                    ),
                    html.Label(
                        [
                            html.Span("Owner:"),
                            dcc.Input(
                                id="apps-camera-control-user",
                                type="text",
                                placeholder="허수아비",
                                readOnly=True,
                                debounce=True,
                            ),
                        ],
                    ),
                ],
                id="apps-camera-control-box",
            ),
        ],
        id="apps-camera-container",
    )


@app.callback(
    Output("apps-camera-ws", "send"),
    Output("apps-camera-control-sn", "value"),
    Output("apps-camera-control-farm", "value"),
    Output("apps-camera-control-user", "value"),
    Output("apps-camera-img", "src"),
    Input("apps-camera-control-sensor", "value"),
)
def select(sid:int):


    if sid is None:
        return no_update, no_update, no_update, no_update

    sensor = _sensors[sid]
    s = sensor.sn
    f = sensor.farm.name
    u = sensor.farm.user.realname
    sleep(0.1)
    return s, s, f, u , f"/assets/img/b2f_640x480.png?{ttime()}"


# region ----[ WebSocket Img ]----

_receive_func = """
//dash not allow async callback
function(msg)
{
    if (msg === undefined) return;

    msg.data.slice(-4).arrayBuffer().then(header =>
    {
        var decoder = new TextDecoder();
        var metaLen = parseInt(decoder.decode(header), 10);
        //console.log("metaLen= " + metaLen);

        msg.data.slice(-metaLen).arrayBuffer().then(meta => 
        {
            const ts = decoder.decode(meta.slice(0, 32));
            const dt = new Date(ts);
            //console.log("ts=" + ts + "  dt=" + dt);

            const sn = decoder.decode(meta.slice(32, - 4));
            //console.log(sn);

            const imgInfo = document.querySelector('#apps-camera-info');
            imgInfo.textContent = sn + " @ " + toLocalISOString(dt); //dt.toString();

            const jpg = msg.data.slice(0, msg.data.size, "image/jpeg");
            const elImg = document.querySelector('#apps-camera-img');
            //elImg.classList.remove("visibily-hidden");
            elImg.src = URL.createObjectURL(jpg);

        });
    });
}
"""
app.clientside_callback(
    _receive_func,
    # Output("apps-camera-img", "src"),
    Input("apps-camera-ws", "message"),
)

# endregion

add_page(layout, "IR Cam")
