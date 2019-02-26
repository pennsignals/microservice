"""Mongo."""

from collections import namedtuple
from contextlib import (
    closing,
    contextmanager,
)
from functools import wraps
from logging import (
    basicConfig,
    # DEBUG,
    getLogger,
    INFO,
)
from sys import stdout
from time import sleep as block
from uuid import uuid4

from pymongo import MongoClient
from pymongo.errors import AutoReconnect

from .core import (
    BACKOFF,
    Configurable,
    RETRIES,
)


basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


def retry_on_reconnect(retries=RETRIES, backoff=BACKOFF):
    """Retry decorator for AutoReconnect.

    The pymongo client does not retry operations even when
        mongo reports auto reconnect is available.

    The obj must have a reconnects property.
    """
    def wrapper(func):
        """Return wrapped method."""
        @wraps(func)
        def wrapped(obj, *args, **kwargs):
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


class Mongo(Configurable):
    """Mongo."""

    @classmethod
    def from_cfg(cls, cfg):
        """Return model from cfg."""
        collection = cfg['collection']
        collection_cls_name = '_Collection' + uuid4().hex

        class Collection(namedtuple(  # pylint: disable=too-few-public-methods
                collection_cls_name, collection.keys())):
            """Collection."""

            @classmethod
            def from_cfg(cls, cfg: dict) -> object:
                """Return collection from cfg."""
                return cls(**cfg)

        kwargs = {
            key: cast(cfg[key])
            for key, cast in (
                ('uri', str),
                ('collection', Collection.from_cfg),
            )}
        return cls(**kwargs)

    def __init__(self, uri: str, collection: dict):
        """Initialize Mongo."""
        self.uri = uri
        self._collection = collection
        self.reconnects = 0

    @contextmanager
    def collection(self):
        """Contextmanager for collection."""
        with self.database() as database:
            kwargs = {
                key: database[value]
                for key, value in self._collection.items()
            }
            yield self._collection.__class__(**kwargs)

    @contextmanager
    def connection(self):
        """Contextmanager for connection."""
        connection = MongoClient(self.uri)
        with closing(connection):
            yield connection

    @contextmanager
    def database(self):
        """Contextmanager for database."""
        with self.connection() as connection:
            database = connection.get_database()
            yield database

    def ping(self):
        """Ping mssql on startup."""
        raise NotImplementedError()  # pragma: no cover
