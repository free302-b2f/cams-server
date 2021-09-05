"""웹소켓 에코 테스터"""

# region ---- imports ----

from apps.imports import *
from dash import no_update

from dash_extensions import WebSocket
import base64
from ws.server import get_ws_info

# from dash_extensions.enrich import (
#     DashProxy,
#     Trigger,
#     TriggerTransform,
#     MultiplexerTransform,
#     ServersideOutputTransform,
#     NoOutputTransform,
# )

# endregion

debug("loading...")

_ws_url, _ = get_ws_info("echo")


def layout():
    debug(layout, f"entering...")
    app.title = "Live Stream Study"

    return html.Div(
        [
            # html.Video(id="home-video", src="/assets/proximity.mp4", controls=True),
            dcc.Input(id="home-input", autoComplete="off", value="a"),
            html.Div(id="home-message", children="-none-"),
            WebSocket(id="home-ws-echo", url=_ws_url),
        ],
        className="home-content",
    )


# region ----[ WebSocket echo ]----

# Send input value using websocket.
send = "function(value){return value;}"
app.clientside_callback(
    send, Output("home-ws-echo", "send"), Input("home-input", "value")
)

# Update div using websocket.
receive = 'function(msg){return "Response from websocket: " + msg.data;}'
app.clientside_callback(
    receive, Output("home-message", "children"), Input("home-ws-echo", "message")
)

# # input --> ws
# @app.callback(Output("home-ws-echo", "send"), Input("home-input", "value"))
# def _send_msg(value: str):
#     if value is None:
#         return no_update
#     return value


# # ws --> div
# @app.callback(Output("home-message", "children"), Input("home-ws", "message"))
# def message(e):
#     if e is None:
#         return "-none-"
#     return e["data"]

# endregion


add_page(layout, "WsTester")

# testing
# layout()
