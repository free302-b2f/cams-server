"""센서 추가 화면"""

from admin._imports import *
from admin._common import *


_name = html.Label(
    [
        html.Span("Sensor Name"),
        html.Span("_", className="material-icons-two-tone"),
        dcc.Input(
            id="admin-manage-add-farm-name",
            type="text",
            maxLength=Sensor.max_name,
            required=True,
        ),
    ],
    className="admin-manage-label",
)

_sn = html.Label(
    [
        html.Span("Sensor SN"),
        html.Span("_", className="material-icons-two-tone"),
        dcc.Input(
            id="admin-manage-add-farm-name",
            type="text",
            maxLength=Sensor.max_sn,
            required=True,
        ),
    ],
    className="admin-manage-label",
)

_desc = html.Label(
    [
        html.Span("Description"),
        html.Span("_", className="material-icons-two-tone"),
        dcc.Input(
            id="admin-manage-add-farm-name",
            type="text",
            maxLength=Sensor.max_desc,
            required=True,
        ),
    ],
    className="admin-manage-label",
)

addSensorSection = html.Section(
    [
        html.Hr(),
        _name,
        _sn,
        _desc,
        buildButtonRow("Add Sensor", "sensor"),
    ],
    className="admin-manage-add-section",
)
