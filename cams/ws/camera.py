"""OpenCV를 이용하여 카메라 설정 및 이미지 추출"""

import os, cv2

# cv2.CAP_MSMF 사용시의 초기화속도 개선: 효과없음. 왜?
_os_opencv_key = "OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"
os.environ[_os_opencv_key] = "0"

# global variables
_camera = None
_empty = bytes(0)


def init():
    """카메라 초기화"""

    global _camera
    release()

    print(f"{__name__}.init(): starting...: {os.environ[_os_opencv_key]}")
    # print(cv2.getBuildInformation())

    # 카메라 초기화 : IR 카메라용 파리미터?
    #_camera = cv2.VideoCapture(0, cv2.CAP_MSMF) # Windows에서 매우 오래걸림. Linux에서는?
    _camera = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Windows에서 빠름
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
    """1개의 프레임을 JPEG 포맷으로 인코딩"""

    global _camera
    success, frame = _camera.read()
    if not success:
        print(f"{__name__}.jpeg(): read() failed.")
        return _empty

    success, buffer = cv2.imencode(".jpg", frame)
    if not success:
        print(f"{__name__}.jpeg(): imencode() failed.")

    bytes = buffer.tobytes()
    return bytes
