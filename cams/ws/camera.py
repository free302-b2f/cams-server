"""OpenCV를 이용하여 카메라 설정 및 이미지 추출"""

import os, cv2, struct
from typing import Any, List
from datetime import datetime, timezone

# cv2.CAP_MSMF 사용시의 초기화속도 개선: 효과없음. 왜?
_os_opencv_key = "OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"
os.environ[_os_opencv_key] = "0"


# region ----[ global variables ]----
_camera = None
_empty = bytes(0)

# ID of camera/sensor/device...
_id = ""
_id_bytes: bytes
_id_len = 0

# 메타 데이터 헤더 길이: 
_header_len = 4

# endregion


def init(id: str = "B2F_CAMs_1000000000001"):
    """카메라 초기화"""

    global _camera, _id, _id_bytes, _id_len
    release()

    # encode id
    _id = id
    _id_bytes = id.encode("utf-8")
    _id_len = len(_id_bytes)


    print(f"{__name__}.init(): starting...: {os.environ[_os_opencv_key]}")
    # print(cv2.getBuildInformation())

    # 카메라 초기화 : IR 카메라용 파리미터?
    # _camera = cv2.VideoCapture(0, cv2.CAP_MSMF) # Windows에서 매우 오래걸림. Linux에서는?
    _camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Windows에서 빠름
    print(f"{__name__}.init(): {_camera = }")

    # 카메라 설정
    _camera.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    _camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)


def release():
    global _camera
    if _camera:
        _camera.release()
        _camera = None


def jpeg() -> bytes:
    """프레임을 JPEG 포맷으로 인코딩"""

    global _camera, _empty
    success, frame = _camera.read()
    if not success:
        print(f"{__name__}.jpeg(): read() failed.")
        return _empty

    # JPEG 인코딩
    success, jpeg = cv2.imencode(".jpg", frame)
    if not success:
        print(f"{__name__}.jpeg(): imencode() failed.")

    buffer = _addMeta(jpeg)

    return buffer


def _addMeta(jpeg):
    """타임스탬프와 장비 아이디를 이미지 데이터 끝에 추가"""

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
    buffer[jpegLen + tsLen :] = _id_bytes   # id
    buffer[jpegLen + tsLen + _id_len :] = headerBytes # header

    return buffer


if __name__ == "__main__":
    init()
    jpeg()
