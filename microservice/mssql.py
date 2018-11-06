"""Mssql."""

from contextlib import (
    closing,
    contextmanager,
)
from functools import wraps
from logging import (  # pylint: disable=unused-import
    basicConfig,
    DEBUG,
    getLogger,
    INFO,
)
from sys import stdout
from time import sleep as block

from pandas import DataFrame
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

from .core import (
    BACKOFF,
    Configurable,
    RETRIES,
)

# pylint: disable=invalid-name
MssqlException = (MssqlDatabaseException, MssqlDriverException)


basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


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


class Mssql(Configurable):
    """Mssql."""

    @classmethod
    def query2df(cls, cursor, query, *args):
        cursor.execute(query, *args)
        columns = (each[0] for each in cursor.description)
        # how to set metadata for null columns?
        # datatypes = (each[1] for each in cursor.description)
        # but these are probably surely mssql datatypes and not python types
        df = DataFrame(cursor.fetchall())
        df.columns = columns
        return df

    def __init__(self, dsn):
        self.dsn = dsn
        self.reconnects = 0

    @contextmanager
    def commit(self):
        """Mssql commit contextmanager."""
        connection = MssqlConnection(*self.dsn)
        logger.info('{"mssql.open"}')
        with closing(connection):
            try:
                with closing(connection.cursor()) as cursor:
                    yield cursor
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                logger.info('{"mssql.close"}')

    @contextmanager
    def rollback(self):
        """Mssql rollback contextmanager."""
        connection = MssqlConnection(*self.dsn)
        logger.info('{"mssql.open"}')
        with closing(connection):
            try:
                with closing(connection.cursor()) as cursor:
                    yield cursor
            finally:
                connection.rollback()
                logger.info('{"mssql.close"}')

    def ping(self):
        """Ping mssql on startup."""
        raise NotImplementedError()
