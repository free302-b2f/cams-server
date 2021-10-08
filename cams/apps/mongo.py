"""MongoDB를 테스트하기 위한 페이지
+ MongoDB에서 하루치의 데이터를 불러와 dash.DataTable 로 출력한다.
+ Db 쿼리 시간과 주요 계산의 소요시간을 측정하여 출력한다.
"""

# region ---- imports ----

from apps.imports import *

# endregion

debug("loading...")
# print(f'{__name__}: {pm_has_c() = }')

# region ---- DB Server & Connection ----

_db = getConfigSection("Mongo")
_mongo = MongoClient(
    f'mongodb://{_db["User"]}:{_db["Pw"]}@{_db["Ip"]}:{_db["Port"]}/{_db["Db"]}',
    document_class=RawBSONDocument,
)
_camsDb = _mongo[_db["Db"]]
debug(f"{_camsDb.list_collection_names()= }")

# endregion

data_columns = [
    "Date",
    "Time",
    "Light",
    "Air_Temp",
    "Leaf_Temp",
    "Humidity",
    "CO2",
    "Dewpoint",
    "EvapoTranspiration",
    "HD",
    "VPD",
]
data_titles = [
    "Date",
    "Time",
    "Light",
    "Tair",
    "Tleaf",
    "RH[%]",
    "CO₂",
    "DP",
    "EvaTrans",
    "HD",
    "VPD",
]
data_types = {x: "float64" for x in data_columns}
meta_columns = ["_id", "SN", "FarmName", "Date", "Time"]
for x in meta_columns:
    data_types[x] = "string"
# data_types['Time'] = 'string'#'timedelta64'
# data_types['Date'] = 'string'#'datetime64'


def build_data_table(df: pd.DataFrame) -> DataTable:
    """pandas.DataFrame을 dash.DataTable로 변환한다."""

    columns = [
        {
            "name": t,
            "id": c,
            "type": "numeric",
            "format": Format(precision=3, scheme=Scheme.decimal_si_prefix),  # fixed)
        }
        for t, c in zip(data_titles, data_columns)
    ]

    table = DataTable(
        id="table",
        columns=columns,
        data=df.to_dict("records"),
        style_cell=dict(textAlign="right", paddingRight="5px", fontFamily="Consolas"),
        style_header=dict(textAlign="center", backgroundColor="lightblue"),
        style_data=dict(backgroundColor="lavender"),
    )
    return table


# @cache.memoize(timeout=30)
def load_data() -> Tuple[List[float], pd.DataFrame]:
    """DB에서 하루동안의 데이터를 불러온다.
    쿼리 시간과 DataFrame 변환시간의 리스트를 생성
    :return: 소요시간과 DataFrame의 튜플"""

    timing = [0, 0]
    startTime = timer()

    sensors = _camsDb["sensors"]

    today = "20211003"  # datetime.now().strftime('%Y%m%d')
    cursor = sensors.find(
        {"SN": "B2F_CAMs_1000000000001", "Date": today},
        # projection={'_id': False, 'FarmName':False, 'SN':False}
    ).sort([("Time", 1)])
    ds = list(cursor)

    timing[0] = round(timer() - startTime, 3)

    startTime = timer()
    df = pd.DataFrame(ds).astype(data_types)  # , copy=False)
    df["time_key"] = [util.parseDate(d, t) for d, t in zip(df["Date"], df["Time"])]
    df.set_index("time_key", inplace=True)
    timing[1] = round(timer() - startTime, 3)

    return (timing, df)


def _avg(arr):
    """숫자형 배열의 평균을 구한다"""

    if arr.name in meta_columns:
        return arr[0]
    # if arr.name == 'Date' or arr.name == 'Time': return arr[0]
    # print(f'_avr(): {arr.name = }')
    avg = np.average(arr)
    return avg


def test_resampling():
    """pands.DataFrame.resample()을 테스트한다"""

    df = load_data()
    debug(test_resampling, f"{df.shape = }")
    df.to_csv("cams_org.txt")

    samples = df.sample(frac=0.1)
    samples.to_csv("cams_sample.txt")

    resample = df.resample("5T", label="left").apply(_avg)
    resample.to_csv("cams_resample.txt")

    return build_data_table(resample)
    # return build_table_figure(df)
    # return generate_table(df)


def layout():
    """Dash의 layout을 설정한다"""

    debug(layout, f"entering...")
    app.title = "B2F - Mongo Tester"

    timing, df = load_data()
    cbc.record_timing("Query", timing[0], "query DB")
    cbc.record_timing("DataFrame", timing[0], "pandas DataFrame")

    startTime = timer()
    dt = build_data_table(df)
    timing.append(round(timer() - startTime, 3))
    cbc.record_timing("DataTable", timing[2], "dash DataTable")

    return html.Div(
        [
            html.H3("Testing Mongo DB"),
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
add_page(layout, "MongoDB", 60)
