from apps.imports import *
from dash import no_update
from dash_extensions import WebSocket

from ws.server import get_ws_info
from db import sensor, user, farm

SENSOR_ID = "B2F_CAMs_1000000000001"
_ws_url = get_ws_info(f"download/{SENSOR_ID}")

_sensors = {s.id:s for s in sensor.all()}
_sensorOptions = [{"label": _sensors[id].sn, "value": id} for id in _sensors]

def layout():
   
    return html.Div(
        [
            html.Div(
                [
                    html.Img(id="apps-camera-img"),
                    html.Div(html.H3("IR Camera View"), id="apps-camera-title"),
                    html.Div(
                        [
                            html.Span("Image Info: "),
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
                                value=_sensorOptions[0]["value"],
                            ),
                        ]
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
    Output("apps-camera-control-farm", "value"),
    Output("apps-camera-control-user", "value"),
    Input("apps-camera-control-sensor", "value"),
)
def select(sid):
    f = _sensors[sid].farm.name
    u = _sensors[sid].farm.user.realname
    return f, u


# region ----[ WebSocket Img ]----

receive = """
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
            let ts = decoder.decode(meta.slice(0, 32));
            var dt = new Date(ts);
            //console.log("ts=" + ts + "  dt=" + dt);

            let sn = decoder.decode(meta.slice(32, - 4));
            //console.log(sn);

            const imgInfo = document.querySelector('#apps-camera-info');
            imgInfo.textContent = sn + " @ " + toLocalISOString(dt); //dt.toString();

            jpg = msg.data.slice(0, msg.data.size, "image/jpeg");
            document.querySelector('#apps-camera-img').src = URL.createObjectURL(jpg);

        });
    });
}
"""
app.clientside_callback(
    receive,
    # Output("apps-camera-img", "src"),
    Input("apps-camera-ws", "message"),
)

# endregion

add_page(layout, "IR Cam")
