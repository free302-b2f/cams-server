"""test """

from apps.imports import *
import db.farm as db
import json


def load_data() -> List[dict]:
    """DB에서 데이터를 불러온다"""

    # 모든 레코드 추출
    models = db.list()
    dics = [m.to_dict() for m in models]

    # 테이블의 필드 이름 추출
    cols = db.Farms.__table__.columns.keys()

    return (cols, dics)


def build_data_table(cols: List[str], data: List[dict]) -> DataTable:
    """pandas.DataFrame을 dash.DataTable로 변환한다."""

    # 메타데이터를 제외한 필드의 형식 지정
    columns = [
        {
            "name": t,
            "id": t,
            # "type": "numeric",
            # "format": Format(precision=3, scheme=Scheme.decimal_si_prefix),  # fixed)
        }
        for t in cols
    ]
    # columns.insert(0, {'name':'Sensor', 'id':'sensor_id'})
    # columns.insert(0, {'name':'Farm', 'id':'farm_id'})

    table = DataTable(
        id="test-farms",
        columns=columns,
        data=data,
        style_cell=dict(textAlign="right", paddingRight="5px", fontFamily="Consolas"),
        style_header=dict(textAlign="center", backgroundColor="lightblue"),
        style_data=dict(backgroundColor="lavender"),
    )

    return table


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")
    app.title = "B2F - TEST"

    cols, df = load_data()
    dt = build_data_table(cols, df)

    return html.Div([html.H3("Testing SqlAlchemy"), html.Hr(), dt])


# layout()#test

# 이 페이지를 메인 라우터에 등록한다.
add_page(layout, "TEST")  # test
# add_page(layout) #test
