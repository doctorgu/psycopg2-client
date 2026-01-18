"""psycopg2_client wrapper"""

from psycopg2_client import Psycopg2Client
from tests.db_settings import db_settings


class DbClient(Psycopg2Client):
    """db client"""

    def __init__(self):
        super().__init__(db_settings=db_settings)
