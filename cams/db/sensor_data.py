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


# region ---- table/column names ----

_tn = "sensor_data"  # table name

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
sd_cols_meta_join = ["group1", "location", "sensor", "time1"]  # 테이블 조인시 컬럼명
sd_cols_meta_raw = ["_id", "FarmName", "SN", "Date"]  # sensor 생성 딕의 키

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
        cursor.execute(f"DROP TABLE IF EXISTS {_tn}")
        pgc.commit()
    finally:
        cursor.close()
        pgc.close()


def f1_clear_data(sid):
    """delete all rows from sensor_data"""

    if sid == None:
        return
    try:
        pgc, cursor = connect()
        sql = cursor.mogrify(f"DELETE FROM {_tn} WHERE sensor_id = %s", (sid,))
        cursor.execute(sql)
        debug(f1_clear_data, f"{sid= } : deleted {cursor.rowcount} rows")
        pgc.commit()
    finally:
        cursor.close()
        pgc.close()


def f1_clear_data_location(locId):
    """delete rows from sensor_data"""

    if locId == None:
        return
    try:
        pgc, cursor = connect()
        sql = cursor.mogrify(f"DELETE FROM {_tn} WHERE location_id = %s", (locId,))
        cursor.execute(sql)
        debug(f1_clear_data_location, f"{locId= } : deleted {cursor.rowcount} rows")
        pgc.commit()
    finally:
        cursor.close()
        pgc.close()


def f2_create_table():
    """메타데이터, 센서테이터 테이블 추가"""

    # 메타메이터 테이블은 별도 생성할것
    # group location sensor app-user

    # 센서데이터 테이블
    create_table = f"""
    CREATE TABLE IF NOT EXISTS {_tn} (
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
        UNIQUE (time, sensor_id)        
    );
    CREATE INDEX ON {_tn} (group_id) INCLUDE (location_id, sensor_id);"""

    # UNIQUE (id, time, sensor_id)

    # 센서테이터에 대한 하이퍼테이블 생성
    create_hypertable = f"""
    SELECT create_hypertable('{_tn}', 'time', 
        partitioning_column => 'sensor_id',
        number_partitions => 100, 
        if_not_exists => TRUE);
    SELECT set_chunk_time_interval('{_tn}', INTERVAL '7 days');
    """

    # 하이퍼테이블 정보 출력
    query_table_info = """
    SELECT h.table_name, c.interval_length FROM _timescaledb_catalog.dimension c
        JOIN _timescaledb_catalog.hypertable h ON h.id = c.hypertable_id;"""

    try:
        pgc, cursor = connect(True)
        cursor.execute(create_table)
        cursor.execute(create_hypertable)
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
    format = f"INSERT INTO {_tn} AS sd ("
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


def InsertRawDics(rawDics, sameSn=None, sameDate: datetime = None):
    """센서 sn에서 생성된 rawDics을 DB에서 그룹/장소/센서 id를 구해서 DB에 추가
    - sameSn : None이 아니면 모든 레코드의 sn이 같은 것으로 간주
    - sameDate : None이 아니면 모든 레코드의 date가 같은 것으로 간주
    """

    try:
        pgc, cursor = connect()

        # 주어진 SN의 센서에 관한 메타 데이터 조회
        def queryMeta(sn):
            sql = cursor.mogrify(
                "SELECT group_id, location_id, id FROM sensor WHERE sn = %s AND active",
                (sn,),
            )
            cursor.execute(sql)
            return cursor.fetchone()

        # 공통 메타 데이터
        if sameSn:
            meta0 = queryMeta(sameSn)
            if meta0 is None:
                return 0

        # DB에 추가
        numRows = 0
        format = _build_insert()
        for dic in rawDics:
            try:
                meta = meta0 if sameSn else queryMeta(dic["SN"])
                if meta is None:
                    break

                dbDate = (
                    sameDate if sameDate else util.parseDate(dic["Date"], dic["Time"])
                )

                values = (*meta, dbDate, *[dic[x] for x in sd_cols_raw])
                sql = cursor.mogrify(format, values)
                cursor.execute(sql)
                numRows+=1
            except:
                error(InsertRawDics, f"failed to insert: {dic['SN']}")
                continue
        pgc.commit()
        return numRows

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

    if sensors == None:
        return
    if len(sensors) == 0:
        return

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
        dates = [start + timedelta(days=x) for x in range(-2, 0)]

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


def _build_select(
    group_id, sensor_id, location_id, startDati, endDati, avgTime: int = 0
):
    """SQL SELECT문 포맷 생성
    - avgTime: 데이터 포인트 간격 (분단위), 0이면 DB값 그대로
    - 포맷과 값 튜플 리턴
    """

    # 메타 컬럼: id 제외
    # sd_cols_meta = ["group_id", "location_id", "sensor_id", "time"]
    metaTables = ["g", "l", "s"]
    metas = sd_cols_meta_join

    tmp = [f"{t}.name AS {c}" for t, c in zip(metaTables, metas)]
    fmt = ",".join(tmp)

    # timeCol = f"time{avgTime}" if avgTime else "time"

    if not avgTime:
        fmt = f"{fmt}, d.time AS {metas[3]}"
        tmp = ",".join([f"d.{x}" for x in sd_cols])
    else:
        fmt = f"{fmt}, time_bucket('{avgTime} minutes', d.time) AS {metas[3]}"
        tmp = ",".join([f"AVG(d.{c}) as {c}" for c in sd_cols])
    fmt = f"{fmt}, {tmp}"

    fmt = f"SELECT {fmt} FROM {_tn} d, app_group g, location l, sensor s"

    # WHERE : date
    fmt = f"{fmt} WHERE (date(d.time) BETWEEN %s AND %s)"
    paramValues = [startDati, endDati]

    # WHERE : meta
    def _param(col, value):
        if value > 0:
            paramValues.append(value)
            return f"{fmt} AND (d.{col} = %s)"
        return fmt

    fmt = _param(sd_cols_meta[0], group_id)
    fmt = _param(sd_cols_meta[1], location_id)
    fmt = _param(sd_cols_meta[2], sensor_id)

    # JOIN: group, location, sensor
    fmt = f"{fmt} AND d.group_id = g.id AND d.location_id = l.id AND d.sensor_id = s.id"

    # group by
    if avgTime:
        fmt = f"{fmt} GROUP BY {','.join(metas)}"

    # order by
    tmp = ",".join([f"{c} ASC" for c in metas])
    fmt = f"{fmt} ORDER BY {tmp}"
    params = tuple(paramValues)

    return fmt, params


def Select(group_id, sensor_id, location_id, startDati, endDati, avgTime: int = 0):
    """sensor_data에서 데이터 추출하여 dataset과 컬럼이름을 리턴"""

    try:
        pgc, cursor = connect()

        fmt, values = _build_select(
            group_id, sensor_id, location_id, startDati, endDati, avgTime
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


def Count(group_id=None, location_id=None, sensor_id=None):
    """주어진 조건의 행 갯수를 리턴"""

    try:
        pgc, cursor = connect()
        fmt = f"SELECT COUNT(*) FROM {_tn} WHERE true"
        if group_id != None:
            fmt = f"{fmt} AND group_id=%(gid)s"
        if location_id != None:
            fmt = f"{fmt} AND location_id=%(lid)s"
        if sensor_id != None:
            fmt = f"{fmt} AND sensor_id=%(sid)s"

        sql = cursor.mogrify(
            fmt, {"gid": group_id, "lid": location_id, "sid": sensor_id}
        )
        # debug(str(sql))

        cursor.execute(sql)
        # numRows = next(iter(cursor.fetchone() or []), None)
        numRows = cursor.fetchone()[0]

        return numRows
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
