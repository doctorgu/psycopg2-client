"""db settings"""

import os
from dotenv import load_dotenv
from psycopg2_client_settings import Psycopg2ClientSettings

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
    before_read_execute=lambda qry_type, params, qry_str, qry_with_value: print(
        f'READ_ROWS_START, QRY_TYPE: "{qry_type}"' f", QRY_WITH_VALUE: {qry_with_value}"
    ),
    after_read_execute=lambda qry_type, duration: print(
        f'READ_ROWS_END, QRY_TYPE: "{qry_type}"' f", DURATION: {duration}"
    ),
    before_update_execute=lambda qry_type, params, params_out, qry_str, qry_with_value: print(
        f'UPDATES_START, QRY_TYPE: "{qry_type}"' f", QRY_WITH_VALUE: {qry_with_value}"
    ),
    after_update_execute=lambda qry_type, row_count, params_out, duration: print(
        f'UPDATES_END, QRY_TYPE: "{qry_type}"' f", DURATION: {duration}"
    ),
)
