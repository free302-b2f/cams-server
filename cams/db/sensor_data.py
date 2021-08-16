"""센서데이터 모델 정의 및 관련 로직"""

from db.imports import *

class Sensor_Data(db.Model):
    """센서 데이터의 DB 모델"""

    # 상수

    # 테이블 컬럼 정의
    id = sc.Column(st.Integer, primary_key=True, autoincrement="auto")
    time = sc.Column(st.DateTime, nullable=False)
    farm_id = sc.Column(st.Integer)
    sensor_id = sc.Column(st.Integer)
    air_temp = sc.Column(st.Float)
    leaf_temp = sc.Column(st.Float)
    humidity = sc.Column(st.Float)
    light = sc.Column(st.Float)
    co2 = sc.Column(st.Float)
    dewpoint = sc.Column(st.Float)
    evapotrans = sc.Column(st.Float)
    hd = sc.Column(st.Float)
    vpd = sc.Column(st.Float)

    def __repr__(self):
        return f"<Farm {self.name}>"


# 모듈 함수 추가
ActionBuilder[Sensor_Data](sys.modules[__name__], Sensor_Data)

# FOREIGN KEY (farm_id) REFERENCES farms (id),
# FOREIGN KEY (sensor_id) REFERENCES sensors (id),
# UNIQUE (time, sensor_id)