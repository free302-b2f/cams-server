"""테스트 위한 json 파일 생성"""


def dump_json():
    """추가할 메타데이터를 json으로 저장"""

    import flask as fl  # db 패키지는 flask app_context 필요
    import utility as util

    app = fl.Flask(__name__)
    app.config["APP_SETTINGS"] = {}
    with app.app_context():
        import db
        from .group import Group
        from .user import AppUser
        from .location import Location
        from .sensor import Sensor
        from .cams_info import Cams
        from ._seed import save_groups_json, SEED_TEST_FILE

        # add group
        group = Group(name="비투팜", desc="(주)비투팜")

        # add user        
        group.users.append(
            AppUser(
                username="b2f-admin",
                password="1q2w",
                email="b2f-admin@b2f.com",
                realname="B2F 관리자",
                level=1,
            )
        )
        group.users.append(
            AppUser(
                username="b2f-user1",
                password="1q2w",
                email="user1@b2f.com",
                realname="B2F User #1",
            )
        )

        # TEST: add location
        loc = Location(name="제1구역", desc="물토란(2022년 2월 파종)")
        loc2 = Location(name="제2구역", desc="개구리밥(2021년 12월 이식)")
        loc3 = Location(name="제3구역", desc="청경채(2021년 5월 파종)")
        group.locations.append(loc)
        group.locations.append(loc2)
        group.locations.append(loc3)

        # add sensor
        sensors = [
            Sensor(sn=f"B2F_CAMs_200000000000{i}", name=f"DrBAE's CAMs #{i}")
            for i in range(1, 5)
        ]
        loc.sensors.extend(sensors[:2])
        loc2.sensors.extend(sensors[2:4])
        group.sensors.extend(sensors)

        groups = [
            group,
            # Group(name="GUEST", desc="게스트 그룹"),
            Group(name="Apple", desc="테스트 그룹1"),
            Group(name="Microsoft", desc="테스트 그룹2"),
            Group(name="Google", desc="테스트 그룹3"),
            Group(name="Amazon", desc="테스트 그룹4"),
        ]
        save_groups_json(groups, SEED_TEST_FILE)


if __name__ == "__main__":

    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    __package__ = "db"

    dump_json()
