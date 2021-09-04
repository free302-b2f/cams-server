"""test """

from datetime import date
from apps.imports import *
import db.farm, db.sensor, db.user, db.sensor_data


def load_data(db) -> List[dict]:
    """DB에서 주어진 테이블의 모든 레코드를 추출한다"""

    # 모든 레코드 추출
    dics = db.allDict()

    # 테이블의 필드 이름 추출
    # cols = list(dics[0])

    return dics


def load_sensor_data(sensorId:int) -> List[dict]:
    """DB에서 sensor_data 테이블의 레코드를 추출한다"""

    sd = db.sensor_data
    SD = db.sensor_data.SensorData

    # 레코드 추출
    start = datetime(2020, 2, 16)
    end = datetime(2020, 2, 17)  # start + timedelta(hours=24)
    dics = sd.listDictBy(
        limit=10000,
        orderBy=[SD.time.desc()],
        filterBy={"sensor_id": sensorId},
        filter=[SD.time >= start, SD.time < end],
    )

    return dics


def build_data_table(
    cols: List[str],
    data: List[dict],
    table_id: str = "test-dt",
    metaCols: List[str] = None,
) -> DataTable:
    """pandas.DataFrame을 dash.DataTable로 변환한다."""

    # 메타데이터를 제외한 필드의 형식 지정
    fmt = {
        "type": "numeric",
        "format": Format(precision=3, scheme=Scheme.decimal_si_prefix),
    }
    columns = [{"name": col, "id": col} for col in cols]
    if metaCols:
        for col in columns:
            if col["id"] not in metaCols:
                col.update(fmt)

    table = DataTable(
        id=table_id,
        columns=columns,
        data=data,
        style_cell=dict(textAlign="right", paddingRight="5px", fontFamily="Consolas"),
        style_header=dict(textAlign="center", backgroundColor="lightskyblue"),
        style_data=dict(backgroundColor="lavender")
    )

    return table


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")
    app.title = "B2F - test sqlalchemy"

    df = load_data(db.user)
    cols = db.user.User.__table__.columns.keys()
    dtUser = build_data_table(cols, df, "test-dt-user")

    df = load_data(db.farm)
    cols = db.farm.Farms.__table__.columns.keys()
    dtFarms = build_data_table(cols, df, "test-dt-farm")

    df = load_data(db.sensor)
    cols = db.sensor.Sensors.__table__.columns.keys()
    dtSensors = build_data_table(cols, df, "test-dt-sensor")

    df = load_sensor_data(df[0]["id"])
    cols = db.sensor_data.SensorData.__table__.columns.keys()
    dtData = build_data_table(
        cols, df, "test-dt-sensor-data", ["id", "time", "farm_id", "sensor_id"]
    )

    return html.Div(
        [
            html.H3("Testing SqlAlchemy"),
            html.Hr(),
            dtFarms,
            dtSensors,
            dtUser,
            dtData,
        ],
        id="apps-test-content",
    )


# layout()#test

# 이 페이지를 메인 라우터에 등록한다.
add_page(layout, "DbTester")  # test
# add_page(layout) #test
