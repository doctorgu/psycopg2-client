"""mock data for bucket"""

from do_test.pytest.mock_data.data_mock_model import ReadRowsMock, UpdatesMock

rows_list: list[ReadRowsMock] = []
out_list: list[UpdatesMock] = []

out_list.append(
    UpdatesMock(
        qry_type="create_tables",
        params={},
        params_ignore=[],
        params_out={},
        row_count=0,
    )
)

out_list.append(
    UpdatesMock(
        qry_type="upsert_user",
        params={"user_id": "gildong.hong", "user_name": "홍길동"},
        params_ignore=[
            "user_id",
            "user_name",
        ],
        params_out={"user_name": ""},
        row_count=1,
    )
)

out_list.append(
    UpdatesMock(
        qry_type="delete_user",
        params={"user_id": "youngja.lee"},
        params_ignore=[],
        params_out={},
        row_count=1,
    )
)
