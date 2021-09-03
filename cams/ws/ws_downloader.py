"""WebSocket 프로토콜을 통해 서버에 저장된 파일을 다운로드

:param _files_per_second: 초당 업로드할 이미지 갯수
:param _ws_host: 웹소켓 서버 DNS or IP
:param _ws_port: 웹소켓 서버 포트

"""

import asyncio, time, threading
from asyncio.tasks import sleep
import websockets
import ws_server

# region ----[ 모듈 설정 변수 ]----

_ws_uri, _ = ws_server.get_ws_info("download")

# endregion


async def _runAsync():
    """웹소켓 서버와 접속하고 서버가 보내는 이미지를 수신한다"""

    print(f"{__name__}._runAsync(): entering...")

    async with websockets.connect(_ws_uri, ping_interval=120, ping_timeout=120) as ws:
        print(f"{ws = }")

        while True:
            try:
                bytes = await ws.recv()
                if len(bytes) > 0:
                    print(f"saving... {round(len(bytes)/1024)} KiB")
                    with open("download.jpg", "wb") as file:
                        file.write(bytes)

            except websockets.exceptions.ConnectionClosedError as ex:
                print(f"{__name__}._runAsync():\n{ex}")
                break

            except Exception as ex:
                print(f"{__name__}._runAsync():\n{ex}")


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
