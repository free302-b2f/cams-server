from dash_html_components.Div import Div
from apps.imports import *
from dash import no_update
from dash_extensions import WebSocket

from ws.server import get_ws_info

SENSOR_ID = "B2F_CAMs_1000000000001"
_ws_url = get_ws_info(f"download/{SENSOR_ID}")


def layout():
    return html.Div(
        [
            html.Img(id="apps-camera-img"),
            html.Div(
                html.H3("Server Push through WebSocket Channel"), id="apps-camera-title"
            ),
            html.Div(
                [
                    html.Span("Image Info: "),
                    html.Span("-none-", id="apps-camera-img-info"),
                ],
                id="apps-camera-img-info-box",
            ),
            WebSocket(id="apps-camera-ws", url=_ws_url),
        ],
        id="apps-camera-img-container",
    )


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

            const imgInfo = document.querySelector('#apps-camera-img-info');
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

add_page(layout, "CamViewer")
