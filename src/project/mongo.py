"""Mongo."""

from __future__ import annotations
from collections import namedtuple
from contextlib import contextmanager
from functools import wraps
from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from sys import stdout
from time import sleep as block
from uuid import uuid4

from pymongo import MongoClient
from pymongo.errors import AutoReconnect

from .configurable import Configurable
from .constants import (
    BACKOFF,
    RETRIES,
)


basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)  # pylint: disable=invalid-name


def retry_on_reconnect(retries=RETRIES, backoff=BACKOFF):
    """Retry decorator for AutoReconnect.

    The pymongo client does not retry operations even when
        mongo reports auto reconnect is available.
    """
    def wrapper(func):
        """Return wrapped method."""
        @wraps(func)
        def wrapped(*args, **kwargs):
            """Return method result."""
            try:
                return func(*args, **kwargs)
            # coverage only with a replicaset and failover.
            except AutoReconnect as retry:
                logger.exception(retry)
                for i in range(retries):
                    try:
                        return func(*args, **kwargs)
                    except AutoReconnect:
                        block(backoff * i)
                raise
        return wrapped
    return wrapper


class Output(Configurable):
    """Output."""

    @classmethod
    def from_cfg(cls, cfg) -> Output:
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

    def __init__(
            self,
            uri: str,
            collection: namedtuple) -> None:
        """Initialize Mongo."""
        self.uri = uri
        self._collection = collection

    @contextmanager
    def collection(self) -> None:
        """Contextmanager for collection."""
        with self.database() as database:
            kwargs = {
                key: database[value]
                for key, value in self._collection._asdict().items()
            }
            yield self._collection.__class__(**kwargs)

    @contextmanager
    def connection(self) -> None:
        """Contextmanager for connection."""
        with MongoClient(self.uri) as connection:
            logger.info('{"mongo": "open"}')
            try:
                yield connection
            finally:
                logger.info('{"mongo": "close"}')

    @contextmanager
    def database(self) -> None:
        """Contextmanager for database."""
        with self.connection() as connection:
            database = connection.get_database()
            logger.info(
                '{"mongo.open": {"database": "%s"}}',
                database.name)
            try:
                yield database
            finally:
                logger.info(
                    '{"mongo.closed": {"database": "%s"}}',
                    database.name)

    def ping(self) -> bool:
        """Ping mssql on startup."""
        raise NotImplementedError()
