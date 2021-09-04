from apps.imports import *
import time, os, threading
from dash import no_update
from dash_extensions import WebSocket
from flask import Response

from ws.ws_server import get_ws_info
from app import wsLock, wsBuffer


_ws_url, _ws_rate = get_ws_info("download")


def layout():
    return html.Div(
        [
            html.H3(
                "left) JPEG bytes -> http:<base16> -> Browser: img.src=multipart/x-mixed-replace"
            ),
            html.H3(
                "right) JPEG bytes -> websocket:bytes -> Browser: img.src=<base64> (server push)"
            ),
            # dbc.Button(
            #     "OPEN CAMERA", id="camera-open-button", value="Open", n_clicks=0
            # ),
            html.Img(id="camera-image", src="/video", alt="-img-", width="45%"),
            html.Img(id="home-img", src="", width="45%", alt="-img-"),
            WebSocket(id="home-ws-img", url=_ws_url),
        ]
    )


# region ----[ WebSocket Img ]----

# receive = """
# function(msg)
# {
#     if (msg === undefined) return;
#     return URL.createObjectURL(msg.data);
# }
# """
# app.clientside_callback(
#     receive,
#     Output("home-img", "src"),
#     Input("home-ws-img", "message"),
# )

# endregion

add_page(layout, "CamViewer")


def gen_frames():

    while True:
        try:
            with wsLock:
                data = wsBuffer[0]
            debug(f"sending... {round(len(data)/1024)} KiB")

        except Exception as ex:
            debug(gen_frames, ex)

        # concat frame one by one and show result
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + data + b"\r\n")
        time.sleep(1 / _ws_rate)


@app.server.route("/video")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")
