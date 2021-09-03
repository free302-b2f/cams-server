"""WebSocket 프로토콜을 통해 서버에 카메라 캡쳐이미지를 업로드

:param _files_per_second: 초당 업로드할 이미지 갯수
:param _ws_host: 웹소켓 서버 DNS or IP
:param _ws_port: 웹소켓 서버 포트

"""

import asyncio, time, threading
from asyncio.tasks import sleep
import websockets

if __name__ == "__main__":
    import sys, os

    if not "app" in sys.modules:
        appPath = os.path.join(sys.path[0], "..")
        sys.path.insert(0, appPath)

    import camera, ws_server
else: 
    from ws import camera, ws_server


# region ----[ 모듈 설정 변수 ]----

_ws_url, _ws_rate = ws_server.get_ws_info("upload")
_counter = 0  # test

# endregion


async def _test_echo(ws) -> str:
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

            await sleep(1.0 / _ws_rate)


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
