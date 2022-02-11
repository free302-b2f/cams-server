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
        from ._seed import save_group_json, SEED_MASTER_FILE, SEED_GUEST_FILE

        # add group
        group = Group(name="MASTER", desc="마스터 그룹")

        # add user
        user = AppUser(
            username="cams",
            password=util.generate_password_hash("1q2w#E$R"),
            email="amadeus.bae@gmail.com",
            realname="B2F Master",
            level=2,  # master
        )
        group.users.append(user)

        # TEST: add location
        loc = Location(name="제1구역", desc="물토란(2022-02-01~)")
        loc2 = Location(name="제2구역", desc="개구리밥(2021-12-01~2022-05-31)")
        group.locations.append(loc)
        group.locations.append(loc2)

        # add sensor
        sensors = [
            Sensor(sn=f"B2F_CAMs_200000000000{i}", name=f"DrBAE's CAMs #{i}")
            for i in range(1, 5)
        ]
        loc.sensors.extend(sensors[:2])
        loc2.sensors.extend(sensors[2:4])
        group.sensors.extend(sensors)

        save_group_json(group, SEED_MASTER_FILE)

        save_group_json(Group(name="GUEST", desc="게스트 그룹"), SEED_GUEST_FILE)


if __name__ == "__main__":

    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    __package__ = "db"

    dump_json()
