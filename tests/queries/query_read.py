"""query for user"""

qry_dic: dict[str, str] = {}


qry_dic.update(
    {
        "read_user_id_all": """
SELECT  user_id
FROM    t_user
"""
    }
)

qry_dic.update(
    {
        "read_user_search": """
SELECT  user_id, user_name, user_rank, insert_time, update_time
FROM    t_user
WHERE   1 = 1
#if user_id
        AND user_id = %(user_id)s
#elif user_name
        AND user_name ILIKE %(user_name)s
#elif user_rank
        AND user_rank <= %(user_rank)s
#endif
"""
    }
)

qry_dic.update(
    {
        "read_user_alias": """
SELECT  user_id "Id|아이디", user_name "Name|이름", user_rank "Rank|순위"
FROM    t_user
WHERE   user_id = %(user_id)s
"""
    }
)

qry_dic.update(
    {
        "read_csv_partial": """
SELECT  row_number() OVER (ORDER BY 1) rnum,
        TO_CHAR(generate_series, 'YYYY년 MM월 DD일') each_day
FROM    generate_series(
            '2001-01-01'::timestamp,
            '2025-12-31'::timestamp,
            '1 day'::interval
        )
"""
    }
)

qry_dic.update(
    {
        "insert_python_join": """
INSERT INTO python_join (
        repository, file_path, fn_name, line_no, join_type,
        left_table, left_column, right_table, right_column
)
SELECT
        %(repository)s, %(file_path)s, %(fn_name)s, %(line_no)s, %(join_type)s,
        %(left_table)s, %(left_column)s, %(right_table)s, %(right_column)s
"""
    }
)
