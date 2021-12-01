"""PostgreSQL: sensor_data 테이블"""

print(f"<{__name__}> loading...")

# region ---- imports ----

if __name__ == "__main__":
    import sys, os

    dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(dir)

from apps._imports import *
import utility as util
from timeit import default_timer as timer
import random

import psycopg2 as pg
import psycopg2.extensions as pge
import psycopg2.extras as pga

from .group import Group
from .location import Location
from .sensor import Sensor

# endregion


# region ---- DB Server & Connection ----

_set = getSettings("Postgres")
_pgc = pg.connect(
    f'postgres://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)

# endregion


def f0_check_connection():
    cursor: pge.cursor = _pgc.cursor()
    cursor.execute("SELECT 'hello world'")
    ds = cursor.fetchone()
    print(ds)
    _pgc.commit()
    cursor.close()
    return ds


def f1_drop_table():
    """drop sensor_data table"""

    cursor: pge.cursor = _pgc.cursor()
    cursor.execute("DROP TABLE IF EXISTS sensor_data")
    _pgc.commit()
    cursor.close()
    pass


def f1_clear_data():
    """delete all rows from sensor_data"""

    cursor: pge.cursor = _pgc.cursor()
    cursor.execute("DELETE FROM sensor_data")
    _pgc.commit()
    cursor.close()
    pass


def f2_create_table():
    """메타데이터, 센서테이터 테이블 추가"""

    # 메타메이터 테이블은 별도 생성할것
    # group location sensor app-user

    # 센서데이터 테이블
    create_sensordata_table = """
    CREATE TABLE IF NOT EXISTS sensor_data (
        id SERIAL, 
        time TIMESTAMPTZ NOT NULL,
        sensor_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        air_temp DOUBLE PRECISION,
        leaf_temp DOUBLE PRECISION,
        humidity DOUBLE PRECISION,
        light DOUBLE PRECISION,
        co2 DOUBLE PRECISION,
        dewpoint DOUBLE PRECISION,
        evapotrans DOUBLE PRECISION,
        hd DOUBLE PRECISION,
        vpd DOUBLE PRECISION,
        FOREIGN KEY (sensor_id) REFERENCES sensor (id),
        FOREIGN KEY (location_id) REFERENCES location (id),
        FOREIGN KEY (group_id) REFERENCES app_group (id),
        UNIQUE (time, sensor_id),
        UNIQUE (id, time, sensor_id)
    );
    CREATE INDEX ON sensor_data (id);"""

    # 센서테이터에 대한 하이퍼테이블 생성
    create_sensordata_hypertable = """
    SELECT create_hypertable('sensor_data', 'time', 
        partitioning_column => 'sensor_id',
        number_partitions => 100, 
        if_not_exists => TRUE);
    SELECT set_chunk_time_interval('sensor_data', INTERVAL '7 days');
    """

    cursor: pge.cursor = _pgc.cursor()
    cursor.execute(create_sensordata_table)
    cursor.execute(create_sensordata_hypertable)
    _pgc.commit()

    # 하이퍼테이블 정보 출력
    query_table_info = """
    SELECT h.table_name, c.interval_length FROM _timescaledb_catalog.dimension c
        JOIN _timescaledb_catalog.hypertable h ON h.id = c.hypertable_id;"""
    cursor.execute(query_table_info)
    ti = cursor.fetchone()
    debug(f"table info: {ti}")

    cursor.close()


def f3_seed(sensors):
    """기본적인 메타데이터 및 랜덤 센서데이터 추가"""

    try:
        cursor: pge.cursor = _pgc.cursor(cursor_factory=pga.DictCursor)

        # # 센서 ID 추출
        # if not sensors:
        #     cursor.execute("SELECT id FROM group limit 1")
        #     gid = [x["id"] for x in cursor.fetchall()][0]
        #     cursor.execute(f"SELECT id FROM sensor WHERE group_id = {gid}")
        #     ids = [x["id"] for x in cursor.fetchall()]

        start = datetime.combine(datetime.now().date(), datetime.min.time())
        dates = [start + timedelta(days=x) for x in range(-7, 1)]

        sql = """INSERT INTO sensor_data 
            (time, sensor_id, location_id, group_id, air_temp, leaf_temp, humidity, 
            light, co2, dewpoint, evapotrans, hd, vpd) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT DO NOTHING"""

        def insert(sid: int, dt: datetime, lid: int, gid: int):
            debug(f"inserting: {sid} @{dt}")
            for x in range(2880):
                light = random.uniform(80, 100) * (
                    dt.hour if dt.hour < 13 else 24 - dt.hour
                )
                cursor.execute(
                    sql,
                    (
                        dt,
                        sid,
                        lid,
                        gid,
                        round(random.uniform(10, 30), 1),  # air temp
                        round(random.uniform(10, 30), 1),  # leaf
                        round(random.uniform(30, 90), 1),  # humidity
                        round(light, 1),  # light
                        round(random.uniform(0, 100), 1),  # co2
                        round(random.uniform(0, 10), 1),  # dewpoint
                        round(random.uniform(0, 10), 1),
                        round(random.uniform(0, 10), 1),
                        round(random.uniform(0, 10), 1),
                    ),
                )
                dt = dt + timedelta(seconds=30)
            _pgc.commit()
            pass

        # 각 센서에 대해 센서데이터 추가
        for s in sensors:
            for d in dates:
                try:
                    insert(s.id, d, s.location_id, s.group_id)
                except:
                    debug(f"failed: {s.id}@{d}")
                    pass
    finally:
        cursor.close()
    pass


def f4_copy_mongo():
    """MonogDB의 센서데이터를 PostgreSQL에 복사한다"""

    from pymongo import MongoClient
    from bson.raw_bson import RawBSONDocument

    # mongo
    set = getSettings("Mongo")
    mc = MongoClient(
        f'mongodb://{set["User"]}:{set["Pw"]}@{set["Ip"]}:{set["Port"]}/{set["Db"]}',
        document_class=RawBSONDocument,
    )
    _sensors = mc[set["Db"]]["sensors"]

    # postgres: sensor 목록
    cursor: pge.cursor = _pgc.cursor(cursor_factory=pga.DictCursor)
    cursor.execute("SELECT id, sn FROM sensor")
    sensorIds = {x["sn"]: x["id"] for x in cursor.fetchall()}
    cursor.close()

    #
    def insert(cursor, record, sensorDic):
        """convert mongodb record to postgresql record"""

        cursor.execute(
            """
            INSERT INTO sensor_data 
            (time, sensor_id, air_temp, leaf_temp, humidity, light, co2, dewpoint, evapotrans, hd, vpd) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (
                util.parseDate(record["Date"], record["Time"]),  # time
                sensorDic[record["SN"]],  # sensor id
                # data_columns = ['Light','Air_Temp','Leaf_Temp','Humidity','CO2','Dewpoint','EvapoTranspiration','HD','VPD']
                record["Air_Temp"],  # air temp
                record["Leaf_Temp"],  # leaf
                record["Humidity"],  # humidity
                record["Light"],  # light
                record["CO2"],  # co2
                record["Dewpoint"],  # dewpoint
                record["EvapoTranspiration"],  # EvapoTranspiration
                record["HD"],  # HD
                record["VPD"],  # VPD
            ),
        )

    # get first last day
    first = _sensors.find().sort([("_id", 1), ("Date", 1)]).limit(1)[0]["Date"]
    last = _sensors.find().sort([("_id", -1), ("Date", -1)]).limit(1)[0]["Date"]

    t1 = util.parseDate(first)
    t2 = util.parseDate(last)
    numDays = (t2 - t1).days
    for d in range(0, numDays):
        date = (t1 + timedelta(days=d)).strftime("%Y%m%d")
        info(f"converting {date}...")

        startTime = timer()
        src = _sensors.find({"Date": date}).sort([("_id", 1)])

        cursor: pge.cursor = _pgc.cursor()
        for record in src:
            insert(cursor, record, sensorIds)
        _pgc.commit()
        cursor.close()

        elapsedTime = round(timer() - startTime, 3)
        info(f" -> {elapsedTime} sec")

    return


if __name__ == "__main__":
    f1_drop_table()
    f2_create_table()
    f3_seed()
    # f3_copy_mongo()
