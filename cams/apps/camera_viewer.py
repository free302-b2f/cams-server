from apps.imports import *
from dash import no_update
from dash_extensions import WebSocket

from ws.server import get_ws_info


_ws_url, _ws_rate = get_ws_info("download")


def layout():
    return html.Div(
        [
            html.H3("Server Push Image Data by WebSocket"),
            html.Img(id="apps-camera-img", src="", width="60%", alt="-img-"),
            html.Div([html.Span("Image Info: "), html.Span(id="apps-camera-img-info")]),
            WebSocket(id="apps-camera-ws", url=_ws_url),
        ]
    )


# region ----[ WebSocket Img ]----

receive = """
function(msg)
{
    if (msg === undefined) return;
    msg.data.slice(-26).arrayBuffer().then(buffer =>
    {
        buffer.slice(0, 4)
        let ts = new Float32Array(buffer.slice(0, 4))[0];
        var dt = new Date(ts);
        console.log(dt);

        let sn = new TextDecoder().decode(buffer.slice(4));
        console.log(sn);

        const imgInfo = document.querySelector('#apps-camera-img-info');
        imgInfo.textContent = sn + " @ " + dt.toLocaleString('ko-KR', { hour12: false });

        document.querySelector('#apps-camera-img').src = URL.createObjectURL(msg.data);
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
