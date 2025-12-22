"""common function for all datalake test"""

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

        qry_str: str
        params: dict[str, any]
        qry_type: str
        method_type: Literal["update", "read", "csv"]
        en: bool = None

        rows: list[dict]
        row: dict
        row_count: int
        _first_fetch_csv: bool = True

        def execute(self, qry_str: str, params: dict[str, any]):
            """execute"""
            self.qry_str = qry_str
            self.params = params

        def set_test_info(
            self,
            qry_type: str,
            method_type: Literal["update", "read", "csv"],
            *,
            en: bool = None,
        ):
            """set info for test only"""

            self.qry_type = qry_type
            self.method_type = method_type
            self.en = en
            if method_type in ("read", "csv"):
                rows = get_rows_by_params(self.qry_type, self.params, self.en)
                row = rows[0] if rows else None
                self.rows = rows
                self.row = row
            elif method_type == "update":
                params_out, row_count = get_out_by_params(self.qry_type, self.params)
                self.row = params_out
                self.row_count = row_count

        def fetchall(self) -> list[dict]:
            """return rows"""
            if self.method_type == "csv":
                if self._first_fetch_csv:
                    self._first_fetch_csv = False
                    return self.rows
                else:
                    return []

            return self.rows

        def fetchone(self) -> dict | None:
            """return row"""
            if self.method_type == "csv":
                if self._first_fetch_csv:
                    self._first_fetch_csv = False
                    return self.row
                else:
                    return None

            return self.row

        def rowcount(self):
            """return row count"""
            return self.row_count

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


def patch_all(mocker):
    """patch functions of object"""

    patch_psycopg2(mocker)
