from typing import Callable
from websockets.exceptions import ConnectionClosed


class WsPool:
    """서버와 연결된 클라이언트 WebSocket 목록유지와 전송기능 구현"""

    def __init__(self, debug: Callable = None, info: Callable = None):
        self._pool = []
        self._debug = debug
        self._info = info

    def debug(self, *msg):
        if self._debug:
            self._debug(*msg)

    def info(self, *msg):
        if self._debug:
            self._debug(*msg)

    async def broadcast(self, message):
        """모든 클라이언트에게 데이터를 전송한다"""

        for ws in self._pool:
            await self._try_send(ws, message)

    async def _try_send(self, ws, message):
        """주어진 웹소켓을 통해 데이터를 전송한다"""

        self.debug(f"sending: {round(len(message)/1024)} KiB")  # test
        try:
            await ws.send(message)
        except ConnectionClosed as ex:
            self.debug(f"ConnectionClosed: {ex}")
            self.remove(ws)
        except Exception as ex:
            self.debug(f"Exception: {ex}")
        if not ws.open or ws.closed:
            self.remove(ws)

    def add(self, ws):
        """클라이언트를 목록에 추가한다"""

        self.debug(f"adding: {ws}")
        self._pool.append(ws)

    def remove(self, ws):
        """클라이언트를 목록에서 제거한다"""

        self.debug(f"removing: {ws}")
        self._pool.remove(ws)
