"""OpenCV를 이용하여 카메라 설정 및 이미지 추출"""

import os, cv2 as cv
import threading, time, queue
from typing import Any, List
from datetime import datetime, timezone

# cv2.CAP_MSMF 사용시의 초기화속도 개선: 효과없음. 왜?
_OS_OPENCV_KEY = "OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"
os.environ[_OS_OPENCV_KEY] = "0"
_FPS = 1


# region ----[ global variables ]----
_camera = None
_empty = bytes(0)
_q = queue.Queue()

# ID of camera/sensor/device...
_id = ""
_id_bytes: bytes
_id_len = 0

# 메타 데이터 헤더 길이:
_header_len = 4

# endregion


def _reader():
    """
        카메라에서 읽은 마지막 데이터만 큐에 유지한다
        버퍼로 인한 지연 문제 해결을 위해 사용 
    """

    global _camera
    while True:
        success, frame = _camera.read()
        if not success:
            print(f"{__name__}._reader(): read() failed.")

        # 큐에 들어있는 기존 프레임 제거
        if not _q.empty():
            try:
                _q.get_nowait()
            except queue.Empty:
                pass
        
        # 큐에 넣기
        _q.put(frame)

        # 읽기 속도 조절
        # time.sleep(1 / _FPS / 10)


def init(id: str):
    """카메라 초기화"""

    global _camera, _id, _id_bytes, _id_len
    release()

    # encode id
    _id = id
    _id_bytes = id.encode("utf-8")
    _id_len = len(_id_bytes)
    
    print(f"{__name__}.init(): <{_id}> starting...")
    # print(cv2.getBuildInformation())

    # 카메라 초기화 : IR 카메라용 파리미터?
    # _camera = cv.VideoCapture(0, cv.CAP_MSMF) # Windows에서 매우 오래걸림. Linux에서는?
    _camera = cv.VideoCapture(0, cv.CAP_DSHOW)  # Windows에서 빠름
    print(f"{__name__}.init(): {_camera = }")

    # 카메라 설정
    _camera.set(cv.CAP_PROP_FRAME_WIDTH, 800)
    _camera.set(cv.CAP_PROP_FRAME_HEIGHT, 600)
    _camera.set(cv.CAP_PROP_BUFFERSIZE, 1)
    # _camera.set(cv.CAP_PROP_FPS, 2)

    # 큐와 쓰레드 초기화
    t = threading.Thread(target=_reader)
    t.daemon = True
    t.start()


def release():
    global _camera
    if _camera:
        _camera.release()
        _camera = None


def jpeg() -> bytes:
    """프레임을 JPEG 포맷으로 인코딩"""

    # JPEG 인코딩
    success, jpeg = cv.imencode(".jpg", _q.get())
    if not success:
        print(f"{__name__}.jpeg(): imencode() failed.")

    return _addMeta(jpeg)


def _addMeta(jpeg):
    """타임스탬프와 장비 아이디를 이미지 데이터 끝에 추가한다"""

    global _id_bytes, _id_len, _header_len
    jpegLen = len(jpeg)

    # 타임스탬프 생성
    ts = datetime.now(timezone.utc).isoformat()
    tsBytes = ts.encode("utf-8")
    tsLen = len(tsBytes)

    # header = 메타 데이터의 바이트 단위 길이를 3글자로 저장
    metaLen = tsLen + _id_len + _header_len
    totalLen = jpegLen + metaLen
    header = f"{{:0>{_header_len}}}".format(metaLen)
    headerBytes = header.encode("utf-8")

    # debug
    print(f"{ts= }, {_id= }, {header= }")
    print(f"{tsLen= }, {_id_len= }, {len(headerBytes)= }")

    # 버퍼 생성 & copy bytes
    buffer = bytearray(totalLen)
    buffer[:] = jpeg.tobytes()  # jpeg
    buffer[jpegLen:] = tsBytes  # timestamp
    buffer[jpegLen + tsLen :] = _id_bytes  # id
    buffer[jpegLen + tsLen + _id_len :] = headerBytes  # header

    return buffer


if __name__ == "__main__":
    # test
    init()
    jpeg()
