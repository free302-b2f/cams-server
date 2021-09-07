from __future__ import annotations
import threading
from typing import Any, Callable, Dict
from websockets.exceptions import ConnectionClosed


class WsPool(object):
    """서버와 연결된 클라이언트 WebSocket 목록유지와 전송기능 구현"""

    def __init__(self):
        self._pool = []
        self._lock = threading.Lock()  # _pool 조작시 사용

    async def broadcast(self, message):
        """모든 클라이언트에게 데이터를 전송한다"""

        # 연결 끊긴 소켓을 풀에서 제거
        with self._lock:
            for ws in self._pool.copy():
                if not ws.open or ws.closed:
                    self._pool.remove(ws)

        # 모든 소켓을 통해 전송
        # TODO: 모든 전송완료 때까지 업로드 중단됨
        #  --> 큐와 쓰레드 이용 백그라운드 처리
        with self._lock:
            for ws in self._pool:
                await self._try_send(ws, message)

    async def _try_send(self, ws, message):
        """주어진 웹소켓을 통해 데이터를 전송한다"""

        # WsPool.debug(f"sending: {round(len(message)/1024)} KiB")  # test
        try:
            await ws.send(message)

        except ConnectionClosed as ex:
            WsPool.debug(f"ConnectionClosed: {ex}")

        except Exception as ex:
            WsPool.debug(f"Exception: {ex}")

    def add(self, ws):
        """클라이언트를 목록에 추가한다"""

        WsPool.info(f"adding: {ws}")
        with self._lock:
            if ws not in self._pool:
                self._pool.append(ws)

    def remove(self, ws):
        """클라이언트를 목록에서 제거한다"""

        WsPool.info(f"removing: {ws}")
        with self._lock:
            if ws not in self._pool:
                self._pool.remove(ws)

    # class variables
    _pools: Dict[int, Any] = dict()
    _lock: threading.Lock = threading.Lock()
    _debug: Callable
    _info: Callable

    @classmethod
    def setLogger(cls, debug: Callable = None, info: Callable = None):
        """로깅 메소드를 설정한다"""

        cls._debug = debug
        cls._info = info

    @classmethod
    def debug(cls, *msg):
        if cls._debug:
            cls._debug(*msg)

    @classmethod
    def info(self, *msg):
        if self._info:
            self._info(*msg)

    @classmethod
    def getPool(cls, id: str) -> WsPool:
        """주어진 아이디의 풀을 리턴, 없으면 생성"""

        try:
            cls._lock.acquire()
            if id not in cls._pools:
                cls._pools[id] = WsPool()
            pool = cls._pools[id]
        finally:
            cls._lock.release()
            return pool
