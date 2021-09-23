import asyncio, threading, websockets
from db import sensor
from typing import Dict, List, Tuple
from websockets.exceptions import ConnectionClosed

from app import error, debug, info, getConfigSection
from ws.pool import WsPool


# TODO: load from appsettings.json
_set = getConfigSection("WebSocket")
_WS_HOST = _set[_set["HostName"]]
_WS_PORT = _set["port"]  # websocket port
_WS_BASE_URL = f"ws://{_WS_HOST}:{_WS_PORT}"
# _WS_RATE = _set["rate"]  # 초당 업/다운로드할 이미지 수


def get_ws_info(path: str) -> str:
    return f"{_WS_BASE_URL}/{path}"


async def _echo(ws):
    
    try:
        async for msg in ws:
            debug(f"echoing: {msg}")  # test
            await ws.send(msg)

    except ConnectionClosed as ex:
        debug(_echo, f"ConnectionClosed: {ex}")

    except Exception as ex:
        error(_echo, ex)
    
    info(_download, f"echo client disconnected")


# WsPool 클래스 초기화
WsPool.setLogger(debug, info)


async def _upload(ws, sensor):
    """웹소켓 수신 데이터를 파일/버퍼에 저장"""

    info(_upload, f"uploader connected to <{sensor}>")
    pool = WsPool.getPool(sensor)  # WsPool 인스턴스 생성

    async for data in ws:
        # debug(f"received: {round(len(data)/1024)} KiB")  # test
        await pool.broadcast(data)  # TODO: wait until all download complete?

    info(_upload, f"uploader disconnected from <{sensor}>")


async def _download(ws):#, sensorId: int):
    """파일/버퍼에서 웹소켓으로 데이터 전송"""

    info(_download, f"downloader connected.")# to <{sensorId}>")
    lastSensor = ""
    
    try:
        async for newSensor in ws:  # 연결유지
            if lastSensor != newSensor:
                if lastSensor: 
                    # WsPool.remove(lastSensor, ws)
                    pool = WsPool.getPool(lastSensor)
                    pool.remove(ws)

                info(_download, f"downloader request: {newSensor}")
                lastSensor = newSensor
                # WsPool.add(newSensor, ws)
                pool = WsPool.getPool(newSensor)
                pool.add(ws)

    except ConnectionClosed as ex:
        debug(_download, f"ConnectionClosed: {ex}")

    except Exception as ex:
        debug(_download, f"Exception: {ex}")

    info(_download, f"downloader disconnected from <{lastSensor}>")
    # WsPool.remove(lastSensor, ws)
    pool = WsPool.getPool(lastSensor)
    pool.remove(ws)


def getSensorId(path: str) -> int:
    """주어진 경로에서 아이디를 추출한다"""

    words = path.split("/")
    if len(words) < 2:
        return "_unknown_"
    else:
        return words[1].strip()


async def _client_handler(ws, path: str):
    # debug(_client_handler, f"{path= }")

    path = path.strip().strip("/")
    if path.startswith("upload"):
        await _upload(ws, getSensorId(path))

    elif path.startswith("download"):
        await _download(ws)#, getSensorId(path))

    else:
        await _echo(ws)


async def _runAsync():
    """웹소켓 서버를 시작한다"""

    debug(_runAsync, f"entering...")
    async with websockets.serve(
        _client_handler, "0.0.0.0", _WS_PORT, ping_interval=120, ping_timeout=120
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
