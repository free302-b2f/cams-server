"""DBMS 초기화 등 """

if __name__ == "__main__":
    import sys, os.path as path

    dir = path.join(path.dirname(__file__), "..")
    sys.path.append(dir)

from apps.imports import *

_set = getConfigSection("Postgres")
_pgc = pg.connect(
    f'postgres://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)


def seed():
    """기본적인 메타데이터 추가"""

    cursor: pge.cursor = _pgc.cursor(cursor_factory=pga.DictCursor)

    # 1개의 농장 추가
    # cursor.execute("INSERT INTO farms (name) VALUES (%s)", ("Bit2Farm KIST",))

    # # 3개의 센서 추가
    # cursor.execute("INSERT INTO sensors (sn) VALUES (%s)", ("B2F_CAMs_1000000000001",))
    # cursor.execute("INSERT INTO sensors (sn) VALUES (%s)", ("B2F_CAMs_1000000000002",))
    # cursor.execute("INSERT INTO sensors (sn) VALUES (%s)", ("B2F_CAMs_1000000000003",))
    # _pgClient.commit()

    # 농장 ID 추출
    cursor.execute("SELECT id FROM farms ORDER BY id DESC LIMIT 1")
    farmId = cursor.fetchone()["id"]

    # 센서 ID 추출
    cursor.execute("SELECT id, sn FROM sensors")
    ids = {x["sn"]: x["id"] for x in cursor.fetchall()}

    start = datetime.combine(datetime.now().date(), time())
    dates = [start + timedelta(days=x) for x in range(-30, 30)]

    sql = """INSERT INTO sensor_data 
        (time, farm_id, sensor_id, air_temp, leaf_temp, humidity, 
        light, co2, dewpoint, evapotrans, hd, vpd) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT DO NOTHING"""

    def insert(id):
        for d in dates:

            debug(f"inserting... : {d}")

            for x in range(2880):
                cursor.execute(
                    sql,
                    (
                        d,
                        farmId,
                        ids[id],
                        round(random.uniform(10, 30), 1),  # air temp
                        round(random.uniform(10, 30), 1),  # leaf
                        round(random.uniform(30, 90), 1),  # humidity
                        round(random.uniform(0, 1000), 1),  # light
                        round(random.uniform(0, 100), 1),  # co2
                        round(random.uniform(0, 10), 1),  # dewpoint
                        round(random.uniform(0, 10), 1),
                        round(random.uniform(0, 10), 1),
                        round(random.uniform(0, 10), 1),
                    ),
                )
                d = d + timedelta(seconds=30)
                pass
            pass  # 2880

            _pgc.commit()  # day
        pass  # -30 ~ +30

    pass

    # 각 센서에 대해 센서데이터 추가
    for id in ids:
        insert(id)
    cursor.close()


def init_tables():
    """DBMS에 테이블을 생성하고 기본 데이터를 추가한다"""

    farms = """DROP TABLE IF EXISTS farms;
        CREATE TABLE farms (
            id SERIAL PRIMARY KEY, 
            name VARCHAR(50)
        );"""

    sensors = """DROP TABLE IF EXISTS sensors;
        CREATE TABLE IF NOT EXISTS sensors (
            id SERIAL PRIMARY KEY, 
            sn VARCHAR(50)
        );"""

    cursor: pge.cursor = _pgc.cursor(cursor_factory=pga.DictCursor)
    cursor.execute(farms)
    cursor.execute(sensors)
    _pgc.commit()
    cursor.close()

    pass


if __name__ == "__main__":
    seed()
