"""센서데이터 모델 정의 및 관련 로직"""

from db.imports import *

db.Model.metadata.reflect(bind=db.engine, schema="db_cams")


class SensorData(db.Model):
    """센서 데이터의 DB 모델"""

    def _reflect() -> sc.Table:
        return sc.Table(
            "sensor_data",
            db.Model.metadata,
            sc.Column("id", st.Integer, primary_key=True, autoincrement="auto"),
            autoload_with=db.engine,
        )

    __table__ = _reflect()

    def __repr__(self):
        return f"<SensorData {self.sensor_id}@{self.time}>"

    def to_dict(self):
        dic = {}
        dic["id"] = self.id
        dic["time"] = self.time
        dic["farm_id"] = self.farm_id
        dic["sendor_id"] = self.sensor_id
        dic["air_temp"] = self.air_temp
        dic["leaf_temp"] = self.leaf_temp
        dic["humidity"] = self.humidity
        dic["light"] = self.light
        dic["co2"] = self.co2
        dic["dewpoint"] = self.dewpoint
        dic["evapotrans"] = self.evapotrans
        dic["hd"] = self.hd
        dic["vpd"] = self.vpd
        return dic


ActionBuilder[SensorData](sys.modules[__name__], SensorData)
