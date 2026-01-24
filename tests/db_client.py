"""psycopg2_client wrapper"""

from psycopg2_client.client import Client
from tests.db_settings import db_settings


class DbClient(Client):
    """db client"""

    def __init__(self):
        super().__init__(db_settings=db_settings)
