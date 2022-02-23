"""마스터계정을 위한 json 파일 생성"""


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
        from ._seed import save_groups_json, SEED_MASTER_FILE

        # add group
        group = Group(id=0, name="MASTER", desc="마스터 그룹", storage_id=0)

        # add user
        group.users.append(
            AppUser(
                username="cams",
                password=util.generate_password_hash("1q2w#E$R"),
                email="amadeus.bae@gmail.com",
                realname="CAMs Master",
                level=2,  # master
            )
        )

        # 센서보관소 위치
        group.locations.append(Location(id=0, name="보관소", desc="유휴센서보관소"))

        groups = [group]
        save_groups_json(groups, SEED_MASTER_FILE)


if __name__ == "__main__":

    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    __package__ = "db"

    dump_json()
