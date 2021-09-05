from apps.imports import *
from dash import no_update
from dash_extensions import WebSocket

from ws.server import get_ws_info


_ws_url, _ws_rate = get_ws_info("download")


def layout():
    return html.Div(
        [
            html.H3(
                "JPEG bytes -> websocket:bytes -> Browser: img.src=<base64> (server push)"
            ),            
            html.Img(id="apps-camera-img", src="", width="50%", alt="-img-"),
            WebSocket(id="apps-camera-ws", url=_ws_url),
        ]
    )


# region ----[ WebSocket Img ]----

receive = """
function(msg)
{
    if (msg === undefined) return;
    return URL.createObjectURL(msg.data);
}
"""
app.clientside_callback(
    receive,
    Output("apps-camera-img", "src"),
    Input("apps-camera-ws", "message"),
)

# endregion

add_page(layout, "CamViewer")
