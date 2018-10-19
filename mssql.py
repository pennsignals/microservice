"""Mssql."""

from collections import namedtuple
from contextlib import contextmanager
from functools import wraps
import logging
from os import stdout

# pylint: disable=no-name-in-module
from pymssql import (  # noqa: N812
    connect as MssqlConnection,
    OperationalError,
)

# pylint: disable=no-name-in-module
from _mssql import (
    MssqlDatabaseException,
    MssqlDriverException,
)

# pylint: disable=invalid-name
MssqlException = (MssqlDatabaseException, MssqlDriverException)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = logging.getLogger(__name__)


RETRIES = 5
BACKOFF = 0.15


def retry_on_operational_error(retries=RETRIES, backoff=BACKOFF):
    """Retry decorator for objects and OperationalErrors.

    The obj must have a reconnects property.
    """
    def wrapper(func):
        """Return wrapped method."""
        @wraps(func)
        def wrapped(obj, *args, **kwargs):
            """Return method result."""
            try:
                return func(obj, *args, **kwargs)
            except OperationalError as retry:
                logger.exception(retry)
                for i in range(retries):
                    obj.reconnects += 1
                    try:
                        return func(obj, *args, **kwargs)
                    except OperationalError:
                        block(backoff * i)
                raise
        return wrapped
    return wrapper


class Mssql:
    """Mssql."""

    def __init__(self, dsn):
        self.dsn = dsn
        self.reconnects = 0

    @contextmanager
    def commit(self):
        """Mssql commit contextmanager."""
        dsn = self._dsn
        with MssqlConnection(*dsn) as connection:
            try:
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    @contextmanager
    def rollback(self):
        """Mssql rollback contextmanager."""
        dsn = self._dsn
        with MssqlConnection(*dsn) as connection:
            try:
                yield connection
            finally:
                connection.rollback()
