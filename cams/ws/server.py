import asyncio, threading, websockets
from typing import List, Tuple
from websockets.exceptions import ConnectionClosed

from app import error, debug, info, getConfigSection
from ws.pool import WsPool


# TODO: load from appsettings.json
_set = getConfigSection("WebSocket")
_ws_host = _set[_set["HostName"]]
_ws_port = _set["port"]  # websocket port
_ws_base_url = f"ws://{_ws_host}:{_ws_port}"
_ws_rate = _set["rate"]  # 초당 업/다운로드할 이미지 수


def get_ws_info(path: str) -> Tuple[str, float]:
    return (f"{_ws_base_url}/{path}", _ws_rate)


_pool: WsPool = WsPool(debug, info)


async def _echo(ws):
    async for msg in ws:
        try:
            debug(f"echoing: {msg}")  # test
            await ws.send(msg)
        except ConnectionClosed as ex:
            error(_echo, ex)
            break
        except Exception as ex:
            error(_echo, ex)
        if not ws.open or ws.closed:
            break


async def _upload(ws) -> bool:
    """웹소켓 수신 데이터를 파일/버퍼에 저장"""

    async for data in ws:
        debug(f"received: {round(len(data)/1024)} KiB")  # test
        try:
            await _pool.broadcast(data)  # TODO: wait until all download complete?

        except ConnectionClosed as ex:
            error(_upload, ex)
            break
        except Exception as ex:
            error(_upload, ex)
        if not ws.open or ws.closed:
            break

    info(_upload, "uploader disconnected")


async def _download(ws):
    """파일/버퍼에서 웹소켓으로 데이터 전송"""

    _pool.add(ws)
    async for data in ws:
        pass


async def _client_handler(ws, path: str):
    debug(_client_handler, f"{path= }")

    if path.startswith("/upload"):
        await _upload(ws)
    elif path.startswith("/download"):
        await _download(ws)
    else:
        await _echo(ws)


async def _runAsync():
    debug(f"{__name__}._runAsync(): entering...")
    async with websockets.serve(
        _client_handler, "0.0.0.0", _ws_port, ping_interval=120, ping_timeout=120
    ) as ws:
        info(f"Websocket server started: {ws.server.sockets[0].getsockname()}")
        await asyncio.Future()  # run forever


def _run():
    asyncio.run(_runAsync())


def run(background=True):

    if background:
        _thread = threading.Thread(target=_run, args=())
        _thread.daemon = True  # Daemonize thread
        _thread.start()  # Start the execution
    else:
        _run()


if __name__ == "__main__":
    run(False)
