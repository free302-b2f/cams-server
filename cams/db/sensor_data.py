"""PostgreSQL + TimescaleDB: sensor_data 테이블"""

# region ---- imports ----

if __name__ == "__main__":
    import sys, os.path as path

    dir = path.join(path.dirname(__file__), "..")
    sys.path.append(dir)

from apps.imports import *

# endregion

debug("loading...")

# region ---- DB Server & Connection ----

_set = getConfigSection("Postgres")
_pgc = pg.connect(
    f'postgres://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)

# endregion


def f1_check_db_connection():
    cursor: pge.cursor = _pgc.cursor()
    cursor.execute("SELECT 'hello world'")
    ds = cursor.fetchone()
    print(ds)
    _pgc.commit()
    cursor.close()
    return ds


def _create_table(cursor):
    """메타데이터, 센서테이터 테이블 추가"""

    # 메타메이터 테이블은 별도 생성할것

    # 센서데이터 테이블
    create_sensordata_table = """
    CREATE TABLE IF NOT EXISTS sensor_data (
        id SERIAL, 
        time TIMESTAMPTZ NOT NULL,
        sensor_id INTEGER,
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


def _seed(cursor):
    """기본적인 메타데이터 및 랜덤 센서데이터 추가"""

    # 메타데이터는 별도 추가할 것

    # 센서 ID 추출
    cursor.execute("SELECT id FROM sensor")
    ids = [x["id"] for x in cursor.fetchall()]

    start = datetime.combine(datetime.now().date(), datetime.min.time())
    dates = [start + timedelta(days=x) for x in range(-30, 30)]

    sql = """INSERT INTO sensor_data 
        (time, sensor_id, air_temp, leaf_temp, humidity, 
        light, co2, dewpoint, evapotrans, hd, vpd) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT DO NOTHING"""

    def insert(id: int, d: datetime):
        debug(f"inserting: {id} @{d}")
        for x in range(2880):
            light = random.uniform(80, 100) * (d.hour if d.hour < 13 else 24 - d.hour)
            cursor.execute(
                sql,
                (
                    d,
                    id,
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
            d = d + timedelta(seconds=30)
        _pgc.commit()
        pass

    # 각 센서에 대해 센서데이터 추가
    for id in ids:
        for d in dates:
            insert(id, d)
    pass


def f2_init_and_seed():
    """DBMS에 기본 테이블을 생성한다"""

    cursor: pge.cursor = _pgc.cursor(cursor_factory=pga.DictCursor)
    _create_table(cursor)
    _seed(cursor)
    cursor.close()


def f3_copy_mongo():
    """MonogDB의 센서데이터를 PostgreSQL에 복사한다"""

    _db = getConfigSection("Mongo")
    _mongoClient = MongoClient(
        f'mongodb://{_db["User"]}:{_db["Pw"]}@{_db["Ip"]}:{_db["Port"]}/{_db["Db"]}',
        document_class=RawBSONDocument,
    )
    _camsDb = _mongoClient[_db["Db"]]
    _sensors = _camsDb["sensors"]

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
    f2_init_and_seed()
    # f3_copy_mongo()
