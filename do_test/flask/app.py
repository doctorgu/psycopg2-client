"""flask app"""

import os
import sys
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

# psycopg2_client
sys.path.append(__file__[0 : __file__.find("psycopg2_client") + len("psycopg2_client")])

# pylint: disable=wrong-import-position
from psycopg2_client import Psycopg2Client
from psycopg2_client_settings import Psycopg2ClientSettings
from do_test.flask.db_client import DbClient

app = Flask(__name__)

load_dotenv()

db_settings = Psycopg2ClientSettings(
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USER"),
    minconn=3,
    maxconn=6,
    connect_timeout=3,
    use_en_ko_column_alias=True,
    use_conditional=True,
)


def get_json(
    *, fn_name: str, message: str | int | dict | list[str] | list[int] | list[dict]
):
    """return json"""
    return jsonify({"fn_name": fn_name, "message": message})


@app.route("/")
def home():
    """home"""

    return render_template("index.html")


@app.route("/create-tables")
def create_tables():
    """create tables"""

    db_client = Psycopg2Client(db_settings=db_settings)
    db_client.update("create_tables", {})
    return get_json(fn_name=create_tables.__name__, message="table created")


@app.route("/upsert-user")
def upsert_user():
    """upsert user"""

    db_client = Psycopg2Client(db_settings=db_settings)

    row_count = db_client.update(
        "upsert_user", {"user_id": "gildong.hong", "user_name": "홍길똥"}
    )

    # affected row count: 1
    return get_json(
        fn_name=upsert_user.__name__, message=f"affected row count: {row_count}"
    )


@app.route("/upsert-user-params-out")
def upsert_user_params_out():
    """upsert user and get parameters"""

    db_client = Psycopg2Client(db_settings=db_settings)

    params_out = {"user_name": ""}
    db_client.update(
        "upsert_user", {"user_id": "gildong.hong", "user_name": "홍길동"}, params_out
    )

    # user_name after update: 홍길동
    return get_json(
        fn_name=upsert_user_params_out.__name__,
        message=f'user_name after update: {params_out["user_name"]}',
    )


@app.route("/upsert-user-list")
def upsert_user_list():
    """upsert user list (one transaction)"""

    db_client = Psycopg2Client(db_settings=db_settings)

    qry_list = [
        ("upsert_user", {"user_id": "sunja.kim", "user_name": "김순자"}),
        ("upsert_user", {"user_id": "malja.kim", "user_name": "김말자"}),
    ]
    row_counts = db_client.updates(qry_list)

    # [1, 1]
    return get_json(fn_name=upsert_user_list.__name__, message=row_counts)


@app.route("/upsert-delete-user-with")
def upsert_delete_user_with():
    """upsert user and delete in with (one transaction)"""

    with Psycopg2Client(db_settings=db_settings) as db_client:
        id_ = "youngja.lee"
        user_name = "이영자"
        db_client.update("upsert_user", {"user_id": id_, "user_name": user_name})

        row_count = db_client.update("delete_user", {"user_id": id_})

        # affected row count: 1
        return get_json(
            fn_name=upsert_delete_user_with.__name__,
            message=f"affected row count: {row_count}",
        )


@app.route("/read-user-one-row")
def read_user_one_row():
    """read first one row"""

    db_client = Psycopg2Client(db_settings=db_settings)

    row = db_client.read_row("read_user_id_all", {})

    # RealDictRow({'user_id': 'gildong.hong'})
    return get_json(fn_name=read_user_one_row.__name__, message=row)


@app.route("/read-user-all-rows")
def read_user_all_rows():
    """read all rows"""

    db_client = Psycopg2Client(db_settings=db_settings)

    rows = db_client.read_rows("read_user_id_all", {})

    # [
    #   RealDictRow({'user_id': 'gildong.hong'}),
    #   RealDictRow({'user_id': 'sunja.kim'}),
    #   RealDictRow({'user_id': 'malja.kim'})
    # ]
    return get_json(fn_name=read_user_all_rows.__name__, message=rows)


@app.route("/read-using-conditional1")
def read_using_conditional1():
    """read using conditional 1 (#if #elif #endif)"""

    db_client = Psycopg2Client(db_settings=db_settings)

    # SELECT  user_id, user_name, insert_time, update_time
    # FROM    t_user
    # WHERE   1 = 1
    #         AND user_id = %(user_id)s
    rows = db_client.read_rows(
        "read_user_search", {"user_id": "gildong.hong", "user_name": ""}
    )
    # ['홍길동']
    return get_json(
        fn_name=read_using_conditional1.__name__,
        message=[row["user_name"] for row in rows],
    )


@app.route("/read-using-conditional2")
def read_using_conditional2():
    """read using conditional 2 (#if #elif #endif)"""

    db_client = Psycopg2Client(db_settings=db_settings)

    # SELECT  user_id, user_name, insert_time, update_time
    # FROM    t_user
    # WHERE   1 = 1
    #         AND user_name ILIKE %(user_name)s
    rows = db_client.read_rows("read_user_search", {"user_id": "", "user_name": "%김%"})
    # ['김순자', '김말자']
    return get_json(
        fn_name=read_using_conditional2.__name__,
        message=[row["user_name"] for row in rows],
    )


@app.route("/read-using-en-ko1")
def read_using_en_ko1():
    """set column user_name by en variable"""

    db_client = Psycopg2Client(db_settings=db_settings)

    # SELECT  user_id "Id", user_name "Name"
    # FROM    t_user
    # WHERE   user_id = %(user_id)s
    rows = db_client.read_rows("read_user_alias", {"user_id": "gildong.hong"}, en=True)
    # [{"Id": "gildong.hong", "Name": "홍길동"}]
    return get_json(fn_name=read_using_en_ko1.__name__, message=rows)


@app.route("/read-using-en-ko2")
def read_using_en_ko2():
    """set column user_name by en variable"""

    db_client = Psycopg2Client(db_settings=db_settings)

    # SELECT  user_id "아이디", user_name "이름"
    # FROM    t_user
    # WHERE   user_id = %(user_id)s
    rows = db_client.read_rows("read_user_alias", {"user_id": "gildong.hong"}, en=False)
    # [{"아이디": "gildong.hong", "이름": "홍길동"}]
    return get_json(fn_name=read_using_en_ko2.__name__, message=rows)


@app.route("/use-db-client")
def use_db_client():
    """use inherited class to not use db_settings every time"""

    db_client = DbClient()
    row = db_client.read_row("read_user_id_all", {})

    # RealDictRow({'user_id': 'gildong.hong'})
    return get_json(fn_name=use_db_client.__name__, message=row)


# flask --app .\do_test\flask\app.py run --debug
