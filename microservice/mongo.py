"""Mongo."""

from functools import wraps
from time import sleep as block

from pymongo import MongoClient
from pymongo.errors import AutoReconnect

from core import (
    BACKOFF,
    RETRIES,
)


def retry_on_reconnect(retries=RETRIES, backoff=BACKOFF):
    """Retry decorator for AutoReconnect.

    The pymongo client does not retry operations even when
        mongo reports auto reconnect is available.

    The obj must have a reconnects property.
    """
    def wrapper(func):
        """Return wrapped method."""
        @wraps(func)
        def wrapped(*args, **kwargs):
            """Return method result."""
            try:
                return func(obj, *args, **kwargs)
            # coverage only with a replicaset and failover.
            except AutoReconnect as retry:
                logger.exception(retry)
                for i in range(retries):
                    obj.reconnects += 1
                    try:
                        return func(obj, *args, **kwargs)
                    except AutoReconnect:
                        block(backoff * i)
                raise
        return wrapped
    return wrapper


class Mongo:

    def __init__(self, uri: str, name: str, collections_map: dict):
        self.uri = uri
        self.collections_map = collections_map
        self.reconnects = 0
        self.collections_cls = namedtuple(name, collections_map.keys())

    @contextmanager
    def collections(self):
        """Collections contextmanager."""
        with self.database() as database:
            kwargs = {
                key: database[value]
                for key, value in self.collections_map
            }
            yield self.collections_cls(**kwargs)

    @contextmanager
    def connection(self):
        """Connection contextmanager."""
        connection = MongoClient(self.uri)
        with closing(connection):
            yield connection

    @contextmanager
    def database(self):
        """Database contextmanager."""
        with self.connection() as connection:
            database = connection.get_database()
            yield database

    def ping(self):
        """Ping mssql on startup."""
        raise NotImplementedError()
