"""common function for all datalake test"""

import json
import re
from typing import Literal
from psycopg2 import pool, sql
from mock_data.data_all import (
    get_rows_by_params,
    get_out_by_params,
)



def patch_psycopg2(mocker):
    """patch psycopg2"""

    class CursorMock:
        """CursorMock"""

        def __init__(self):
            self.qry_str = ""
            self.qry_type = ""
            self.func_type: Literal["update", "read", "csv"] = "read"
            self.params: dict[str, any] = {} # type: ignore
            self.en: bool = False

            self.rows: list[dict] = []
            self.row: dict | None = None
            self.rowcount: int = 0
            self._first_fetch_csv: bool = True

        def execute(self, qry_str: str, params: dict[str, any]): # type: ignore
            """execute"""

            def get_header() -> dict[Literal["qry_type", "func_type", "en"], any]: # type: ignore
                ret = re.match(r"/\*(.+)\*/", qry_str)
                if not ret:
                    raise ValueError("no header in query")

                header = ret.group(1)
                info = json.loads(header)
                return info

            def set_test_info(
                qry_type: str,
                func_type: Literal["update", "read", "csv"],
                en: bool = False,
            ):
                """set info for test only"""

                self.qry_type = qry_type
                self.func_type = func_type
                self.en = en
                if func_type in ("read", "csv"):
                    rows = get_rows_by_params(self.qry_type, self.params, self.en)
                    row = rows[0] if rows else None
                    self.rows = rows
                    self.row = row
                elif func_type == "update":
                    params_out, row_count = get_out_by_params(
                        self.qry_type, self.params
                    )
                    self.row = params_out
                    self.rowcount = row_count

            self.qry_str = qry_str
            self.params = params

            header = get_header()
            set_test_info(header["qry_type"], header["func_type"], header["en"])

        def fetchall(self) -> list[dict]:
            """return rows"""
            if self.func_type == "csv":
                if self._first_fetch_csv:
                    self._first_fetch_csv = False
                    return self.rows
                else:
                    return []

            return self.rows

        def fetchone(self) -> dict | None:
            """return row"""
            if self.func_type == "csv":
                if self._first_fetch_csv:
                    self._first_fetch_csv = False
                    return self.row
                else:
                    return None

            return self.row

        def close(self):
            """close"""

    class ConnectionMock:
        """ConnectionMock"""

        def __enter__(self):
            """enter"""
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            """exit"""

        def cursor(self, **_) -> CursorMock:
            """return CursorMock"""
            return CursorMock()

        def commit(self):
            """commit"""

        def rollback(self):
            """rollback"""

    class ThreadedConnectionPoolMock:
        """ThreadedConnectionPoolMock"""

        minconn: int
        maxconn: int
        conn: ConnectionMock

        def __init__(self, minconn, maxconn, **_):
            """init"""

            self.minconn = minconn
            self.maxconn = maxconn
            self.conn = ConnectionMock()

        def getconn(self) -> ConnectionMock:
            """return conn"""
            return self.conn

        def putconn(self, _):
            """put conn"""

        def closeall(self):
            """close all"""

    class PoolMock:
        """PoolMock"""

        # pylint:disable=invalid-name
        def ThreadedConnectionPool(self, minconn, maxconn, **kwargs):
            """ThreadedConnectionPool"""
            return ThreadedConnectionPoolMock(
                minconn=minconn, maxconn=maxconn, **kwargs
            )

    class SqlMock2:
        """SqlMock2"""

        string: str

        def __init__(self, string: str):
            self.string = string

        def as_string(self, _):
            """as_string"""
            return self.string

    class SqlMock:
        """SqlMock"""

        # pylint: disable=invalid-name
        def SQL(self, string: str):
            """SQL"""
            return SqlMock2(string)

    pool_mock = PoolMock()
    mocker.patch.object(
        pool, "ThreadedConnectionPool", side_effect=pool_mock.ThreadedConnectionPool
    )

    sql_mock = SqlMock()
    mocker.patch.object(sql, "SQL", side_effect=sql_mock.SQL)
