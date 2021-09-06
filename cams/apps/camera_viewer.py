from apps.imports import *
from dash import no_update
from dash_extensions import WebSocket

from ws.server import get_ws_info


_ws_url = get_ws_info("download")


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
            //imgInfo.textContent = sn + " @ " + dt.toLocaleString('ko-KR', { hour12: false });
            imgInfo.textContent = sn + " @ " + dt.toString();

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
