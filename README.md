# psycopg2_client

Psycopg2 helper function to run PostgreSQL query

## Usage

- create query in queries directory

```python
qry_dic.update(
    {
        "read_user_id_all": """
SELECT  user_id
FROM    t_user
"""
    }
)
```

- set database information

```python
db_settings = Psycopg2ClientSettings(
    password="0000",
    host="127.0.0.1",
    port=5432,
    database="postgres",
    user="postgres",
    minconn=3,
    maxconn=6,
    connect_timeout=3,
    use_en_ko_column_alias=True,
    use_conditional=True,
)
```

- call query with user_name and parameters

```python
db_client = Psycopg2Client(db_settings=db_settings)

row = db_client.read_row("read_user_id_all", {})

# RealDictRow({'user_id': 'gildong.hong'})
print(row)
```

## update & updates

```python
# define
qry_dic.update(
    {
        "upsert_user": """
WITH t AS (
    INSERT INTO t_user
        (
            user_id, user_name
        )
    VALUES
        (
            %(user_id)s, %(user_name)s
        )
    ON CONFLICT (user_id)
    DO UPDATE
    SET     user_name = %(user_name)s,
            update_time = NOW()
    RETURNING user_name
)
SELECT  user_name
FROM    t;
"""
    }
)
```

- `update` runs one CUD query and returns row counts affected

```python
    row_count = db_client.update(
        "upsert_user", {"user_id": "gildong.hong", "user_name": "홍길똥"}
    )

    # affected row count: 1
    print("affected row count:", row_count)
```

- `update` can return output parameter if params_out parameter passed

```python
    params_out = {"user_name": ""}
    db_client.update(
        "upsert_user", {"user_id": "gildong.hong", "user_name": "홍길동"}, params_out
    )

    # user_name after update: 홍길동
    print("user_name after update:", params_out["user_name"])
```

- `updates` runs multiple CUD query and returns each row counts affected in `List`

```python
    qry_list = [
        ("upsert_user", {"user_id": "sunja.kim", "user_name": "김순자"}),
        ("upsert_user", {"user_id": "malja.kim", "user_name": "김말자"}),
    ]
    row_counts = db_client.updates(qry_list)

    # [1, 1]
    print(row_counts)
```

## single transaction with `with` statement

- `with` statement can be used to group multiple `read_row`, `read_rows`, `update` or `updates` in single transaction

```python
    with Psycopg2Client(db_settings=db_settings) as db_client:
        id_ = "youngja.lee"
        user_name = "이영자"
        db_client.update("upsert_user", {"user_id": id_, "user_name": user_name})

        row_count = db_client.update("delete_user", {"user_id": id_})

        # affected row count: 1
        print("affected row count:", row_count)
```

## read_row & read_rows

- read_row only returns first one row

```python
    row = db_client.read_row("read_user_id_all", {})

    # RealDictRow({'user_id': 'gildong.hong'})
    print(row)
```

- read_rows returns all rows

```python
    rows = db_client.read_rows("read_user_id_all", {})

    # [
    #   RealDictRow({'user_id': 'gildong.hong'}),
    #   RealDictRow({'user_id': 'sunja.kim'}),
    #   RealDictRow({'user_id': 'malja.kim'})
    # ]
    print(rows)
```

## conditional

- `#if`, `#elif`, `#endif` can be used to cut off SQL string by condition when `use_conditional` parameter of `db_settings` is True

```python
# define
qry_dic.update(
    {
        "read_user_search": """
SELECT  user_id, user_name, insert_time, update_time
FROM    t_user
WHERE   1 = 1
#if user_id
        AND user_id = %(user_id)s
#elif user_name
        AND user_name ILIKE %(user_name)s
#endif
"""
    }
)
```

- `#if` part used becuase user_id has value

```python
    # SELECT  user_id, user_name, insert_time, update_time
    # FROM    t_user
    # WHERE   1 = 1
    #         AND user_id = %(user_id)s
    rows = db_client.read_rows(
        "read_user_search", {"user_id": "gildong.hong", "user_name": ""}
    )
    # ['홍길동']
    print([row["user_name"] for row in rows])
```

- `#elif` part used because only user_name has value

```python
    # SELECT  user_id, user_name, insert_time, update_time
    # FROM    t_user
    # WHERE   1 = 1
    #         AND user_name ILIKE %(user_name)s
    rows = db_client.read_rows("read_user_search", {"user_id": "", "user_name": "%김%"})
    # ['김순자', '김말자']
    print([row["user_name"] for row in rows])
```

## column name by langauge

- column name can be changed by `en` parameter when `use_en_ko_column_alias` parameter of `db_settings` is True

```python
# define
qry_dic.update(
    {
        "read_user_alias": """
SELECT  user_id "Id|아이디", user_name "Name|이름"
FROM    t_user
WHERE   user_id = %(user_id)s
"""
    }
)
```

- fist part of `en|ko` used

```python
    # SELECT  user_id "Id", user_name "Name"
    # FROM    t_user
    # WHERE   user_id = %(user_id)s
    rows = db_client.read_rows("read_user_alias", {"user_id": "gildong.hong"}, en=True)
    # [{"Id": "gildong.hong", "Name": "홍길동"}]
    print(json.dumps(rows, ensure_ascii=False))
```

- second part of `en|ko` used

```python
    # SELECT  user_id "아이디", user_name "이름"
    # FROM    t_user
    # WHERE   user_id = %(user_id)s
    rows = db_client.read_rows("read_user_alias", {"user_id": "gildong.hong"}, en=False)
    # [{"아이디": "gildong.hong", "이름": "홍길동"}]
    print(json.dumps(rows, ensure_ascii=False))
```

## Q&A

- Q: is it safe from SQL injection when using conditional?

- A: yes, you can only use number, string(enclosed with `'` or `"`), Python operator and paramter name in conditional line or error raised
