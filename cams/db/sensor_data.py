"""PostgreSQL: sensor_data 테이블 관련 기능"""

print(f"<{__name__}> loading...")

# region ---- imports ----

if __name__ == "__main__" or not __package__:
    # 단독실행시 db 패키지 초기화 생략 (flask context 없이)
    import sys, os.path as path

    dir = path.dirname(path.dirname(__file__))
    sys.path.insert(0, dir)
    from _postgresql import connect
else:
    from ._postgresql import connect

from apps._imports import *
import utility as util
from timeit import default_timer as timer
import random

import psycopg2 as pg
import psycopg2.extensions as pge
import psycopg2.extras as pga

# from .group import Group
# from .location import Location
# from .sensor import Sensor

# endregion


# region ---- column names ----

# 측정값 컬럼 목록
# mongodb는 대소문자를 구별한다.. dict라서?
sd_cols_raw = [
    "Air_Temp",
    "Leaf_Temp",
    "Humidity",
    "Light",
    "CO2",
    "Dewpoint",
    "EvapoTranspiration",
    "HD",
    "VPD",
]
sd_cols = [
    "air_temp",
    "leaf_temp",
    "humidity",
    "light",
    "co2",
    "dewpoint",
    "evapotranspiration",
    "hd",
    "vpd",
]
# 메타 컬럼 목록 ~ string type?
# sd_cols_meta = ["id", "group_id", "location_id", "sensor_id", "time"]
sd_cols_meta = ["group_id", "location_id", "sensor_id", "time"]

# endregion


def f0_check_connection():

    try:
        pgc, cursor = connect()
        cursor.execute("SELECT 'hello world'")
        ds = cursor.fetchone()
        print(ds)
    finally:
        cursor.close()
        pgc.close()


def f1_drop_table():
    """drop sensor_data table"""

    try:
        pgc, cursor = connect()
        cursor.execute("DROP TABLE IF EXISTS sensor_data")
        pgc.commit()
    finally:
        cursor.close()
        pgc.close()


def f1_clear_data():
    """delete all rows from sensor_data"""

    try:
        pgc, cursor = connect()
        cursor.execute("DELETE FROM sensor_data")
        pgc.commit()
    finally:
        cursor.close()
        pgc.close()


def f2_create_table():
    """메타데이터, 센서테이터 테이블 추가"""

    # 메타메이터 테이블은 별도 생성할것
    # group location sensor app-user

    # 센서데이터 테이블
    create_sensordata_table = """
    CREATE TABLE IF NOT EXISTS sensor_data (
        id SERIAL, 
        group_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        sensor_id INTEGER NOT NULL,
        time TIMESTAMPTZ NOT NULL,
        air_temp DOUBLE PRECISION,
        leaf_temp DOUBLE PRECISION,
        humidity DOUBLE PRECISION,
        light DOUBLE PRECISION,
        co2 DOUBLE PRECISION,
        dewpoint DOUBLE PRECISION,
        evapotranspiration DOUBLE PRECISION,
        hd DOUBLE PRECISION,
        vpd DOUBLE PRECISION,
        FOREIGN KEY (group_id) REFERENCES app_group (id),
        FOREIGN KEY (location_id) REFERENCES location (id),
        FOREIGN KEY (sensor_id) REFERENCES sensor (id),
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

    # 하이퍼테이블 정보 출력
    query_table_info = """
    SELECT h.table_name, c.interval_length FROM _timescaledb_catalog.dimension c
        JOIN _timescaledb_catalog.hypertable h ON h.id = c.hypertable_id;"""

    try:
        pgc, cursor = connect(True)
        cursor.execute(create_sensordata_table)
        cursor.execute(create_sensordata_hypertable)
        pgc.commit()

        cursor.execute(query_table_info)
        ti = cursor.fetchone()
        debug(f"table info: {ti}")
        pgc.commit()
    finally:
        cursor.close()
        pgc.close()


def _build_insert() -> str:
    """SQL INSERT문 생성 - id를 제외한 모든 컬럼의 데이터를 추가하는 포맷"""

    # 메타 컬럼과 측정값 컬럼
    cols = sd_cols_meta + sd_cols
    format = "INSERT INTO sensor_data AS sd ("
    tmp = ",".join(cols)
    format = f"{format} {tmp} ) VALUES ("
    tmp = ",".join(["%s" for c in cols])
    format = f"{format} {tmp} )"

    # 중복시 덮어쓰기
    format = f"{format} ON CONFLICT (time, sensor_id) DO UPDATE SET "
    tmp = ",".join([f"{c}=EXCLUDED.{c}" for c in cols])
    format = f"{format} {tmp}"

    return format


def InsertRawDic(rawDic):
    """센서에서 생성된 rawDic을 DB에서 그룹/장소/센서 id를 구해서 DB에 추가"""

    try:
        pgc, cursor = connect()

        # 주어진 SN의 센서에 관한 메타 데이터 조회
        sn = rawDic["SN"]
        dati = util.parseDate(rawDic["Date"], rawDic["Time"])
        cursor.execute(
            f"SELECT group_id, location_id, id FROM sensor WHERE sn = '{sn}'"
        )
        meta = cursor.fetchone()

        # 센서 항목명을 DB 컬럼이름으로 변환
        # dic = {c: rawDic[r] for c, r in zip(sd_cols, sd_cols_raw)}

        # DB에 추가
        values = (*meta, dati, *[rawDic[x] for x in sd_cols_raw])
        sql = cursor.mogrify(_build_insert(), values)
        cursor.execute(sql)

        pgc.commit()

    finally:
        cursor.close()
        pgc.close()


def InsertRawDics(rawDics, sameSn=None, sameDate=None):
    """센서 sn에서 생성된 rawDics을 DB에서 그룹/장소/센서 id를 구해서 DB에 추가
    - sameSn : None이 아니면 모든 레코드의 sn이 같은 것으로 간주
    - sameDate : None이 아니면 모든 레코드의 date가 같은 것으로 간주
    """

    try:
        pgc, cursor = connect()

        # 주어진 SN의 센서에 관한 메타 데이터 조회
        def queryMeta():
            cursor.execute(
                f"SELECT group_id, location_id, id FROM sensor WHERE sn = '{sameSn}'"
            )
            return cursor.fetchone()

        # 공통 메타 데이터
        meta = queryMeta()
        dbDate = sameDate.strftime("%Y%m%d")

        # DB에 추가
        sql = cursor.mogrify(_build_insert())

        for dic in rawDics:
            dati = util.parseDate(dbDate if sameDate else dic["Date"], dic["Time"])
            values = (
                *(meta if sameSn else queryMeta()),
                dati,
                *[dic[x] for x in sd_cols_raw],
            )
            cursor.execute(sql, values)

        pgc.commit()

    finally:
        cursor.close()
        pgc.close()


def _insert_random(cursor: pge.cursor, gid: int, lid: int, sid: int, dt: datetime):
    """sensor_data테이블에 하루치 랜덤 레코드를 추가"""

    info(f"inserting: {sid} @{dt}")
    sql = cursor.mogrify(_build_insert())
    for x in range(2880):
        light = random.uniform(80, 100) * (dt.hour if dt.hour < 13 else 24 - dt.hour)

        cursor.execute(
            sql,
            (
                gid,
                lid,
                sid,
                dt,
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
    cursor.connection.commit()

    pass


def f3_seed(sensors):
    """기본적인 메타데이터 및 랜덤 센서데이터 추가"""

    try:
        pgc, cursor = connect(True)

        # 센서 ID 추출
        if not sensors:
            debug("no sensors, exting...")
            return
            cursor.execute("SELECT id FROM group limit 1")
            gid = [x["id"] for x in cursor.fetchall()][0]
            cursor.execute(f"SELECT id FROM sensor WHERE group_id = {gid}")
            ids = [x["id"] for x in cursor.fetchall()]

        start = datetime.combine(datetime.now().date(), datetime.min.time())
        dates = [start + timedelta(days=x) for x in range(-7, 0)]

        # 각 센서에 대해 센서데이터 추가
        for s in sensors:
            for d in dates:
                try:
                    _insert_random(cursor, s.group_id, s.location_id, s.id, d)
                except:
                    debug(f"failed: {s.id}@{d}")
                    pass
    finally:
        cursor.close()
        pgc.close()
    pass


def _build_select(group_id, sensor_id, location_id, start, end, avgTime: int = 0):
    """SQL SELECT문 포맷 생성
    - avgTime: 데이터 포인트 간격 (분단위), 0이면 DB값 그대로
    - 포맷과 값 튜플 리턴
    """

    # 메타 컬럼: id제외 모든 컬럼
    # sd_cols_meta = ["group_id", "location_id", "sensor_id", "time"]
    metas = list(sd_cols_meta[0:3])
    fmt = ",".join(metas)
    colTime = f"time{avgTime}" if avgTime else "time"
    metas.append(colTime)

    if not avgTime:
        fmt = f"{fmt}, time"
        tmp = ",".join(sd_cols)
    else:
        fmt = f"{fmt}, time_bucket('{avgTime} minutes', time) AS {colTime}"
        tmp = ",".join([f"AVG({c}) as {c}" for c in sd_cols])
    fmt = f"{fmt}, {tmp}"
    fmt = f"SELECT {fmt} FROM sensor_data"

    # WHERE : date
    fmt = f"{fmt} WHERE (date(time) BETWEEN %s AND %s)"
    paramValues = [start, end]

    # WHERE : meta
    def _param(name, value):
        if value > 0:
            paramValues.append(value)
            return f"{fmt} AND ({name} = %s)"
        return fmt

    fmt = _param(sd_cols_meta[0], group_id)
    fmt = _param(sd_cols_meta[1], location_id)
    fmt = _param(sd_cols_meta[2], sensor_id)

    # group by
    if avgTime:
        fmt = f"{fmt} GROUP BY {','.join(metas)}"

    # order by
    tmp = ",".join([f"{c} ASC" for c in metas])
    fmt = f"{fmt} ORDER BY {tmp}"
    params = tuple(paramValues)

    return fmt, params


def Select(group_id, sensor_id, location_id, start, end, avgTime: int = 0):
    """select form sensor_data"""

    try:
        pgc, cursor = connect()

        fmt, values = _build_select(
            group_id, sensor_id, location_id, start, end, avgTime
        )

        sql = cursor.mogrify(fmt, values)
        # debug(str(sql))

        cursor.execute(sql)
        ds = cursor.fetchall()
        cols = [x.name for x in cursor.description]

        return ds, cols
    finally:
        cursor.close()
        pgc.close()


if __name__ == "__main__":
    """pg connection/cursor test"""

    def test_pgc():
        pgc, cursor = connect()
        with pgc:
            with cursor:
                print(f"{pgc.closed=} {cursor.closed=}")

            print(f"{pgc.closed=} {cursor.closed=}")

            cursor.close()  # cursor.close()는 with에의해 호출되지 않음
            print(f"{pgc.closed=} {cursor.closed=}")

        print(f"{pgc.closed=} {cursor.closed=}")

    # test_pgc()

    def test_select():
        d = datetime.now()
        _build_select(0, 1, 1, d, d, 0)
        _build_select(0, 1, 1, d, d, 5)
        _build_select(1, 1, 1, d, d, 5)
        pass

    test_select()

    # f1_drop_table()
    # f2_create_table()
    # f3_seed()
    # f3_copy_mongo()
