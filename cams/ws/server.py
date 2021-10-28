import asyncio, threading, websockets, json, logging, os, sys
from typing import Any, Dict, List, Tuple
from websockets.exceptions import ConnectionClosed

from pool import WsPool

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))
_logger.setLevel("DEBUG")

_set: Any = None
_baseDir = os.path.dirname(__file__)
_setFile = os.path.join(_baseDir, "ws_settings.json")
with open(_setFile, "r", encoding="utf-8") as fp:
    _set = json.load(fp)["WebSocket"]

_WS_HOST = _set[_set["HostName"]]
_WS_PORT = _set["port"]
_WS_BASE_URL = f"ws://{_WS_HOST}:{_WS_PORT}"
_WS_SAVE_DIR = ""


def get_ws_info(path: str) -> str:
    return f"{_WS_BASE_URL}/{path}"


# WsPool 클래스 초기화
def debug(msg):
    _logger.debug(msg)


def info(msg):
    _logger.info(msg)


def error(msg):
    _logger.error(msg)


WsPool.setLogger(debug, info)


async def _echo(ws):

    try:
        async for msg in ws:
            debug(f"echoing: {msg}")  # test
            await ws.send(msg)

    except ConnectionClosed as ex:
        debug(f"ConnectionClosed: {ex}")

    except Exception as ex:
        error(ex)

    info(f"echo client disconnected")


async def _upload(ws, sensorSn):
    """웹소켓 수신 데이터를 파일/버퍼에 저장"""

    info(f"uploader connected to <{sensorSn}>")
    # pool = WsPool.getPool(sensorSn)  # WsPool 인스턴스 생성

    jpgFile = os.path.join(_WS_SAVE_DIR, f"{sensorSn}.jpg")

    async for data in ws:
        # debug(f"received: {round(len(data)/1024)} KiB")  # test
        # await pool.broadcast(data)  # TODO: wait until all download complete?
        info(f"saving {round(len(data)/1024)} KiB to <{jpgFile}>")
        try:
            with open(jpgFile, "wb") as f:
                f.write(data)
        except:
            error(f"fail to write: <{jpgFile}>")
            pass

    info(f"uploader disconnected from <{sensorSn}>")


async def _download(ws, sensorId: int):
    """파일/버퍼에서 웹소켓으로 데이터 전송"""

    info("downloader connected.")  # to <{sensorId}>")

    lastSensor = ""

    def connect(lastSensor: str, newSensor: str) -> str:
        if lastSensor:
            # WsPool.remove(lastSensor, ws)
            pool = WsPool.getPool(lastSensor)
            pool.remove(ws)

        if newSensor:
            info(f"downloader request: {newSensor}")
            # lastSensor = newSensor
            pool = WsPool.getPool(newSensor)
            pool.add(ws)

        return newSensor

    try:
        lastSensor = connect(lastSensor, sensorId)

        async for newSensor in ws:  # 연결유지
            lastSensor = connect(lastSensor, newSensor)

    except ConnectionClosed as ex:
        debug(f"ConnectionClosed: {ex}")

    except Exception as ex:
        debug(f"Exception: {ex}")

    info(f"downloader disconnected from <{lastSensor}>")
    pool = WsPool.getPool(lastSensor)
    pool.remove(ws)


def getSensorSn(path: str) -> int:
    """주어진 경로에서 아이디를 추출한다"""

    words = path.split("/")
    if len(words) < 2:
        return ""
    else:
        return words[1].strip()


async def _client_handler(ws, path: str):
    # debug(_client_handler, f"{path= }")

    path = path.strip().strip("/")
    if path.startswith("upload"):
        await _upload(ws, getSensorSn(path))

    elif path.startswith("download"):
        await _download(ws, getSensorSn(path))

    else:
        await _echo(ws)


async def _runAsync():
    """웹소켓 서버를 시작한다"""

    debug(f"entering...")
    async with websockets.serve(
        _client_handler, "0.0.0.0", _WS_PORT, ping_interval=120, ping_timeout=120
    ) as ws:
        info(f"Websocket server started: {ws.server.sockets[0].getsockname()}")
        await asyncio.Future()  # run forever


def _run():
    asyncio.run(_runAsync())


def run(save_dir: str, background=True):

    global _WS_SAVE_DIR
    _WS_SAVE_DIR = save_dir

    if background:
        _thread = threading.Thread(target=_run, args=())
        _thread.daemon = True  # Daemonize thread
        _thread.start()  # Start the execution
    else:
        _run()


if __name__ == "__main__":
    import os

    baseDir = os.path.dirname(__file__)
    dir = os.path.join(baseDir, "..", "static", "ircam")
    run(dir, False)
