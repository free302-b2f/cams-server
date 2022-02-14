"""마스터계정을 위한 json 파일 생성"""


def dump_json():
    """추가할 메타데이터를 json으로 저장"""

    import flask as fl  # db 패키지는 flask app_context 필요
    import utility as util

    app = fl.Flask(__name__)
    with app.app_context():
        import db
        from .group import Group
        from .user import AppUser
        from .location import Location
        from .sensor import Sensor
        from .cams_info import Cams
        from ._seed import save_groups_json, SEED_MASTER_FILE

        # add group
        masterGroup = Group(name="비투팜", desc="(주)비투팜")

        # add user
        user = AppUser(
            username="cams",
            password=util.generate_password_hash("1q2w#E$R"),
            email="amadeus.bae@gmail.com",
            realname="B2F Master",
            level=2,  # master
        )
        masterGroup.users.append(user)

        # TEST: add location
        loc = Location(name="제1구역", desc="물토란(2022년 2월 파종)")
        loc2 = Location(name="제2구역", desc="개구리밥(2021년 12월 이식)")
        masterGroup.locations.append(loc)
        masterGroup.locations.append(loc2)

        # add sensor
        sensors = [
            Sensor(sn=f"B2F_CAMs_200000000000{i}", name=f"DrBAE's CAMs #{i}")
            for i in range(1, 5)
        ]
        loc.sensors.extend(sensors[:2])
        loc2.sensors.extend(sensors[2:4])
        masterGroup.sensors.extend(sensors)

        groups = [
            masterGroup,
            Group(name="GUEST", desc="게스트 그룹"),
            Group(name="TEST-1", desc="(주)테스트"),
            Group(name="TEST-2", desc="테스트 그룹2"),
            Group(name="TEST-3", desc="테스트 그룹3"),
        ]
        save_groups_json(groups, SEED_MASTER_FILE)


if __name__ == "__main__":

    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    __package__ = "db"

    dump_json()
