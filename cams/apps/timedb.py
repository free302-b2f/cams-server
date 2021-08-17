"""PostgreSQL + TimescaleDB를 테스트하기 위한 페이지
+ DB에서 하루치의 데이터를 불러와 dash.DataTable 로 출력한다.
+ Db 쿼리 시간과 주요 계산의 소요시간을 측정하여 출력한다.
"""

# region ---- imports ----

from apps.imports import *

# endregion

debug("loading...")

# region ---- DB Server & Connection ----

_db = getConfigSection("Postgres")
_pgClient = pg.connect(
    f'postgres://{_db["User"]}:{_db["Pw"]}@{_db["Ip"]}:{_db["Port"]}/{_db["Db"]}'
)

# endregion


# region ---- init & seed ----


def f1_check_db_connection():
    cursor: pge.cursor = _pgClient.cursor()
    cursor.execute("SELECT 'hello world'")
    ds = cursor.fetchone()
    print(ds)
    _pgClient.commit()
    cursor.close()
    return ds


def f2_init_and_seed():
    """DBMS에 기본 테이블을 생성한다"""

    def create_hypertable(cursor):
        """메타데이터, 센서테이터 테이블 추가"""

        # 농장, 센서 테이블
        query_create_sensors_table = """
        CREATE TABLE IF NOT EXISTS farms (
            id SERIAL PRIMARY KEY, 
            name VARCHAR(50));
        CREATE TABLE IF NOT EXISTS sensors (
            id SERIAL PRIMARY KEY, 
            sn VARCHAR(50)            
        );"""

        # 센서데이터 테이블
        query_create_sensordata_table = """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id SERIAL, 
            time TIMESTAMPTZ NOT NULL,
            farm_id INTEGER,
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
            FOREIGN KEY (farm_id) REFERENCES farms (id),
            FOREIGN KEY (sensor_id) REFERENCES sensors (id),
            UNIQUE (time, sensor_id),
            UNIQUE (id, time, sensor_id)
        );
        CREATE INDEX ON sensor_data (id);"""

        # 센서테이터에 대한 하이퍼테이블 생성
        query_create_sensordata_hypertable = """
        SELECT create_hypertable('sensor_data', 'time', 
            partitioning_column => 'sensor_id',
			number_partitions => 100, 
            if_not_exists => TRUE);
        SELECT set_chunk_time_interval('sensor_data', INTERVAL '7 days');
        """
        cursor.execute(query_create_sensors_table)
        cursor.execute(query_create_sensordata_table)
        cursor.execute(query_create_sensordata_hypertable)
        _pgClient.commit()

        # 하이퍼테이블 정보 출력
        query_table_info = """
        SELECT h.table_name, c.interval_length FROM _timescaledb_catalog.dimension c
            JOIN _timescaledb_catalog.hypertable h ON h.id = c.hypertable_id;"""
        cursor.execute(query_table_info)
        ti = cursor.fetchone()
        debug(f"table info: {ti}")

    def seed(cursor):
        """기본적인 메타데이터 추가"""

        # 1개의 농장 추가
        cursor.execute("INSERT INTO farms (name) VALUES (%s)", ("Bit2Farm KIST",))

        # 3개의 센서 추가
        cursor.execute(
            "INSERT INTO sensors (sn) VALUES (%s)", ("B2F_CAMs_1000000000001",)
        )
        cursor.execute(
            "INSERT INTO sensors (sn) VALUES (%s)", ("B2F_CAMs_1000000000002",)
        )
        cursor.execute(
            "INSERT INTO sensors (sn) VALUES (%s)", ("B2F_CAMs_1000000000003",)
        )
        _pgClient.commit()

        # 농장 ID 추출
        cursor.execute("SELECT id FROM farms ORDER BY id DESC LIMIT 1")
        farmId = cursor.fetchone()["id"]

        # 센서 ID 추출
        cursor.execute("SELECT id, sn FROM sensors")
        ids = {x["sn"]: x["id"] for x in cursor.fetchall()}

        # 각 센서에 대해 센서데이터 추가
        for id in ids:
            for x in range(0, 0):
                cursor.execute(
                    """
                INSERT INTO sensor_data 
                (time, farm_id, sensor_id, air_temp, leaf_temp, humidity, light, co2, dewpoint, evapotrans, hd, vpd) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        datetime.now() + timedelta(0, 0, x),
                        farmId,
                        id,
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

        _pgClient.commit()

    cursor: pge.cursor = _pgClient.cursor(cursor_factory=pga.DictCursor)
    create_hypertable(cursor)
    seed(cursor)
    cursor.close()


#f2_init_and_seed()
# endregion


def f2_copy_mongo():
    """MonogDB의 센서데이터를 PostgreSQL에 복사한다"""

    _db = getConfigSection("Mongo")
    _mongoClient = MongoClient(
        f'mongodb://{_db["User"]}:{_db["Pw"]}@{_db["Ip"]}:{_db["Port"]}/{_db["Db"]}',
        document_class=RawBSONDocument,
    )
    _camsDb = _mongoClient[_db["Db"]]
    _sensors = _camsDb["sensors"]

    cursor: pge.cursor = _pgClient.cursor(cursor_factory=pga.DictCursor)
    cursor.execute("SELECT id FROM farms ORDER BY id DESC LIMIT 1")
    farmId = cursor.fetchone()["id"]
    cursor.execute("SELECT id, sn FROM sensors")
    sensorIds = {x["sn"]: x["id"] for x in cursor.fetchall()}
    cursor.close()

    #
    def insert(cursor, farmId, record, sensorDic):
        """convert mongodb record to postgresql record"""
        cursor.execute(
            """
            INSERT INTO sensor_data 
            (farm_id, time, sensor_id, air_temp, leaf_temp, humidity, light, co2, dewpoint, evapotrans, hd, vpd) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (
                farmId,
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

    t1 = datetime(2020, 2, 10) #util.parseDate(first)
    t2 = datetime(2020, 2, 20)#util.parseDate(last)
    numDays = (t2 - t1).days
    for d in range(0, numDays):
        date = (t1 + timedelta(days=d)).strftime("%Y%m%d")
        info(f"converting {date}...")

        startTime = timer()
        src = _sensors.find({"Date": date}).sort([("_id", 1)])

        cursor: pge.cursor = _pgClient.cursor()
        for record in src:
            insert(cursor, farmId, record, sensorIds)
        _pgClient.commit()
        cursor.close()

        elapsedTime = round(timer() - startTime, 3)
        info(f" -> {elapsedTime} sec")

    return


#f2_copy_mongo() #test


# region ---- view ----


def f3_load_data() -> Tuple[List[float], pd.DataFrame]:
    """DB에서 하루동안의 데이터를 불러온다.
    쿼리 시간과 DataFrame 변환시간의 리스트를 생성
    :return: 소요시간과 DataFrame의 튜플"""

    # 모든 센서의 ID 추출
    cursor: pge.cursor = _pgClient.cursor(cursor_factory=pga.DictCursor)
    cursor.execute("SELECT id, sn FROM sensors")
    sensorIds = [x["id"] for x in cursor.fetchall()]
    cursor.close()

    # 테이블의 필드 이름 추출
    cursor: pge.cursor = _pgClient.cursor()
    cursor.execute("select * from sensor_data where false;")
    cols = [x.name for x in cursor.description]

    timing = [0, 0]

    startTime = timer()

    # 첫번째 센서의 2020-02-16 데이터 추출
    start = datetime(2020, 2, 16).date()  # datetime.now().strftime('%Y-%m-%d')
    #end = start + timedelta(hours=23, minutes=59, seconds=59, microseconds=999999)
    sql = cursor.mogrify(
        """select * from sensor_data 
        WHERE (sensor_id = %s) AND (date(time) = %s)
        ORDER BY time DESC LIMIT 10000""",
        (sensorIds[0], start),
    )
    debug(f"{sql}")

    cursor.execute(sql)
    data = cursor.fetchall()
    timing[0] = round(timer() - startTime, 3)

    # 변환: pandas time series
    startTime = timer()
    df = pd.DataFrame(data)
    if len(data) > 0:
        df.columns = cols

    df["Time"] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in df["time"]]
    df.set_index("time", inplace=True)
    timing[1] = round(timer() - startTime, 3)

    return (timing, df)


# f3_load_data()#test


def build_data_table(df: pd.DataFrame) -> DataTable:
    """pandas.DataFrame을 dash.DataTable로 변환한다."""

    # 메타데이터를 제외한 필드의 형식 지정
    col_names = list(df.columns)
    col_names.remove("Time")
    col_names.remove("farm_id")
    col_names.remove("sensor_id")
    col_names.insert(0, "Time")
    columns = [
        {
            "name": t,
            "id": t,
            "type": "numeric",
            "format": Format(precision=3, scheme=Scheme.decimal_si_prefix),  # fixed)
        }
        for t in col_names
    ]
    columns.insert(0, {"name": "Sensor", "id": "sensor_id"})
    columns.insert(0, {"name": "Farm", "id": "farm_id"})

    table = DataTable(
        id="sensors",
        columns=columns,
        data=df.to_dict("records"),
        style_cell=dict(textAlign="right", paddingRight="5px", fontFamily="Consolas"),
        style_header=dict(textAlign="center", backgroundColor="lightblue"),
        style_data=dict(backgroundColor="lavender"),
    )

    return table


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")
    app.title = "B2F - TimeDB Tester"

    timing, df = f3_load_data()
    cbc.record_timing("Query", timing[0], "query DB")
    cbc.record_timing("DataFrame", timing[0], "pandas DataFrame")

    startTime = timer()
    dt = build_data_table(df)
    timing.append(round(timer() - startTime, 3))
    cbc.record_timing("DataTable", timing[2], "dash DataTable")

    return html.Div(
        [
            html.H3("Testing PostgreSQL TimesacleDB"),
            html.Hr(),
            html.Listing(
                util.formatTiming(
                    request, [_db["Name"], _db["Ip"], _db["Port"]], timing, df.shape
                ),
                className="log-listing",
            ),
            dt,
        ]
    )


# 이 페이지를 메인 메뉴바에 등록한다.
add_page(layout, "PostgreSQL", 30)
# layout();#test

# endregion
