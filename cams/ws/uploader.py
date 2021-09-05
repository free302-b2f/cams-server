"""WebSocket 프로토콜을 통해 서버에 카메라 캡쳐이미지를 업로드

:param WS_HOST: 웹소켓 서버 DNS name or IP
:param WS_PORT: 웹소켓 서버 포트
:param WS_RATE: 초당 업로드할 이미지 갯수
"""

import asyncio, time, threading
from asyncio.tasks import sleep
import websockets # pip install websockets
import camera


# region ----[ 모듈 설정 변수 ]----

#TODO: load from config file
WS_HOST = "localhost"
# WS_HOST = "bit2farm.iptime.org"
WS_PORT = 28765
WS_RATE = 30

_ws_url = f"ws://{WS_HOST}:{WS_PORT}/upload"
_counter = 0  # test

# endregion


async def _testEcho(ws) -> str:
    """서버에 테스트 메시지를 보내고 응답을 받는다"""

    global _counter
    _counter += 1
    await ws.send(f"{_counter}")
    res = await ws.recv()
    return res


async def _sendFile(ws):
    """카메라에서 이미지를 추출하여 웹소켓을 통해 전송한다"""

    bytes = camera.jpeg()
    if len(bytes) > 0:
        print(f"uploading... {round(len(bytes)/1024)} KiB")
        await ws.send(bytes)


def _saveFile():
    """카메라에서 이미지를 추출하여 파일로 저장한다"""

    bytes = camera.jpeg()
    if len(bytes) > 0:
        print(f"saving... {len(bytes)/1024}KiB")
        with open("test.jpg", "wb") as file:
            file.write(bytes)


async def _runAsync():
    """웹소켓 서버와 접속하고 카메라 이미지를 계속 업로드한다"""

    print(f"{__name__}._runAsync(): entering...")

    camera.init()
    async with websockets.connect(_ws_url, ping_interval=120, ping_timeout=120) as ws:
        print(f"{ws = }")

        while True:
            try:
                await _sendFile(ws)

            except websockets.exceptions.ConnectionClosedError as ex:
                print(f"{__name__}._runAsync():\n{ex}")
                break

            except Exception as ex:
                print(f"{__name__}._runAsync():\n{ex}")

            await sleep(1.0 / WS_RATE)


def _run():
    asyncio.run(_runAsync())


def run(background=True):
    """업로드를 수행하는 백그라운드 쓰레드를 실행한다."""

    if background:
        _thread = threading.Thread(target=_run, args=())
        _thread.daemon = True
        _thread.start()
    else:
        _run()


if __name__ == "__main__":
    run(False)
