import asyncio, threading, websockets
from typing import List, Tuple
from app import error, debug, info, getConfigSection

# TODO: load from appsettings.json
_ws_host = "localhost"
# _ws_host = "bit2farm.iptime.org"
_ws_port = 28765  # websocket port
_ws_base_url = f"ws://{_ws_host}:{_ws_port}"
_ws_rate = 30  # 초당 업/다운로드할 이미지 수


def get_ws_info(path: str) -> Tuple[str, float]:
    return (f"{_ws_base_url}/{path}", _ws_rate)


async def _echo(ws):
    async for msg in ws:
        try:
            debug(f"echoing: {msg}")  # test
            await ws.send(msg)
        except websockets.exceptions.ConnectionClosedError as ex:
            error(_echo, ex)
            break
        except Exception as ex:
            error(_echo, ex)
        if not ws.open or ws.closed:
            break


async def _upload(ws) -> bool:
    """웹소켓 수신 데이터를 파일/버퍼에 저장"""

    async for data in ws:
        debug(f"writing... {round(len(data)/1024)} KiB")  # test
        try:
            with _lock:
                _buffer[0] = data

        except websockets.exceptions.ConnectionClosedError as ex:
            error(_upload, ex)
            break
        except Exception as ex:
            error(_upload, ex)
        if not ws.open or ws.closed:
            break


async def _download(ws):
    """파일/버퍼에서 웹소켓으로 데이터 전송"""

    while True:
        with _lock:
            data = _buffer[0]

        try:
            debug(f"sending... {round(len(data)/1024)} KiB")
            await ws.send(data)
        except websockets.exceptions.ConnectionClosedError as ex:
            error(_download, ex)
            break
        except Exception as ex:
            error(_download, ex)
        if not ws.open or ws.closed:
            break
        await asyncio.tasks.sleep(1.0 / _ws_rate)


async def _client_handler(ws, path):
    global _thread, _lock, _buffer
    debug(_client_handler, f"{path= }")

    if path == "/upload":
        await _upload(ws)
    elif path == "/download":
        await _download(ws)
    else:
        await _echo(ws)


async def _runAsync():
    print(f"{__name__}._runAsync(): entering...")
    async with websockets.serve(
        _client_handler, "0.0.0.0", _ws_port, ping_interval=120, ping_timeout=120
    ):
        await asyncio.Future()  # run forever


def _run():
    asyncio.run(_runAsync())


_lock: threading.Lock = None
_buffer: List[bytearray] = None


def run(lock: threading.Lock, buffer: List[bytearray] = None, background=True):
    global _thread, _lock, _buffer
    _lock = lock
    _buffer = buffer

    if background:
        _thread = threading.Thread(target=_run, args=())
        _thread.daemon = True  # Daemonize thread
        _thread.start()  # Start the execution
    else:
        _run()


if __name__ == "__main__":
    from app import wsBuffer

    run(threading.Lock(), wsBuffer, False)
