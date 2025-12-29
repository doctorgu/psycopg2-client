"""psycopg2_client wrapper"""

import sys

# psycopg2-client
sys.path.append(__file__[0 : __file__.find("psycopg2-client") + len("psycopg2-client")])

# pylint: disable=wrong-import-position
from psycopg2_client import Psycopg2Client
from tests.db_settings import db_settings


class DbClient(Psycopg2Client):
    """db client"""

    def __init__(self):
        super().__init__(db_settings=db_settings)
