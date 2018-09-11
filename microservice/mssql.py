"""Mssql."""

from collections import namedtuple
from contextlib import closing
from functools import wraps
from time import sleep as block

# pylint: disable=no-name-in-module
from pymssql import (  # noqa: N812
    connect as MssqlConnection,
    OperationalError,
    # output as mssql_output,
)

# pylint: disable=no-name-in-module
from _mssql import (
    MssqlDatabaseException,
    MssqlDriverException,
)

# pylint: disable=invalid-name
MssqlException = (MssqlDatabaseException, MssqlDriverException)

from .core import (
    BACKOFF,
    RETRIES,
)


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

    def ping(self):
        """Ping mssql on startup."""
        raise NotImplementedError()
