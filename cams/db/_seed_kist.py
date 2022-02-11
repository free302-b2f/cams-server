"""KIST 메타 데이터를 위한 json 파일 생생"""


def dump_json():
    """추가할 메타데이터를 json으로 저장"""

    import flask as fl

    app = fl.Flask(__name__)
    with app.app_context():
        import db
        from .group import Group
        from .user import AppUser
        from .location import Location
        from .sensor import Sensor
        from .cams_info import Cams
        from ._seed import save_group_json, SEED_GROUP_FILE

        # add group
        group = Group(name="PHENO", desc="KIST Pheno 그룹")

        # add user
        # pw = util.generate_password_hash("kist1966!!!")
        user = AppUser(
            username="pheno",
            password="kist1966!!!",
            email="kist-pheno@gmail.com",
            realname="Pheno KIST",
            level=1,  # group admin
        )
        group.users.append(user)

        # add location #1
        loc = Location(name="제1동 제1구역", desc="작물1 (2021년 5월 파종)")
        group.locations.append(loc)

        # add sensor
        sensors = [
            Sensor(sn=f"B2F_CAMs_100000000000{i}", name=f"Sensor {i}") for i in range(1, 3)
        ]
        loc.sensors.extend(sensors)
        group.sensors.extend(sensors)

        # add location #2
        loc = Location(name="제1동 제2구역", desc="작물2 (2021년 12월 파종)")
        group.locations.append(loc)

        # add sensor
        sensors = [
            Sensor(sn=f"B2F_CAMs_100000000000{i}", name=f"Sensor {i}") for i in range(3, 7)
        ]
        loc.sensors.extend(sensors)
        group.sensors.extend(sensors)

        save_group_json(group, SEED_GROUP_FILE)


if __name__ == "__main__":

    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    __package__ = "db"
    
    dump_json()
