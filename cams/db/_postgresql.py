"""Postgresql 연결을 위한 공통 기능"""

import utility as util
import psycopg2 as pg
import psycopg2.extensions as pge
import psycopg2.extras as pga
from datetime import date, datetime, time, timedelta, timezone


def connect():
    """설정파일에서 DB설정을 읽어와 연결하고 커서를 리턴"""

    set = util.loadAppSettings("Postgres")
    pgc = pg.connect(
        f'postgres://{set["User"]}:{set["Pw"]}@{set["Ip"]}:{set["Port"]}/{set["Db"]}'
    )
    cursor = pgc.cursor(cursor_factory=pga.DictCursor)
    return pgc, cursor

    