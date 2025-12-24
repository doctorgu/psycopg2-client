"""call pytest_configure"""

import os
import sys


def pytest_configure():
    """
    pytest provides special function called `pytest_configure`
    called when pytest initialzed for configuring custom settings
    """
    os.environ["APP_ENV"] = "test"  # Setting test environment

    # psycopg2_client
    sys.path.append(
        __file__[0 : __file__.find("psycopg2_client") + len("psycopg2_client")]
    )


# -s: print to console
# pytest do_test/pytest --cov=app --cov-report term --cov-report xml
