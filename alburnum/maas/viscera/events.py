"""Objects for events."""

__all__ = [
    "Events",
]

from datetime import datetime
import enum
from functools import partial
import logging
from typing import (
    Iterable,
    Union,
)
from urllib.parse import (
    parse_qs,
    urlparse,
)

import pytz

from . import (
    Object,
    ObjectField,
    ObjectSet,
    ObjectType,
)
from ..utils.typecheck import typed

#
# The query API call returns:
#
#     dict(
#         count=displayed_events_count,
#         events=[...],
#         next_uri=next_uri,
#         prev_uri=prev_uri,
#     )
#
# An event looks like:
#
#     dict(
#         node=event.node.system_id,
#         hostname=event.node.hostname,
#         id=event.id,
#         level=event.type.level_str,
#         created=event.created.strftime('%a, %d %b. %Y %H:%M:%S'),
#         type=event.type.description,
#         description=event.description
#     )
#
# Notes:
# 1. displayed_events_count is len(events). In other words, superfluous.
#


class Level(enum.IntEnum):
    """Logging levels used in MAAS.

    They happen to correspond to levels in the `logging` module.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def normalise(cls, level):
        """Convert the given level into a `Level`.

        :param level: A `Level` instance, a string that matches the name of a
            level, or an integer matching the value of a level.
        :raise ValueError: If the level cannot be found.
        """
        try:
            return cls[level]
        except KeyError:
            return cls(level)


class EventsType(ObjectType):
    """Metaclass for `Events`."""

    Level = Level

    @typed
    def query(
            cls, *,
            hostnames: Iterable[str]=None,
            domains: Iterable[str]=None,
            zones: Iterable[str]=None,
            macs: Iterable[str]=None,
            system_ids: Iterable[str]=None,
            agent_name: str=None,
            level: Union[Level, int, str]=None,
            before: int=None,
            after: int=None,
            limit: int=None):
        """Query MAAS for matching events."""

        if before is not None and after is not None:
            raise ValueError("Specify either `before` or `after`, not both.")

        params = {}

        if hostnames is not None:
            params["hostname"] = list(hostnames)
        if domains is not None:
            params["domain"] = list(domains)
        if zones is not None:
            params["zone"] = list(zones)
        if macs is not None:
            params["mac_address"] = list(macs)
        if system_ids is not None:
            params["id"] = list(system_ids)
        if agent_name is not None:
            params["agent_name"] = [agent_name]
        if level is not None:
            level = Level.normalise(level)
            params["level"] = [level.name]
        if before is not None:
            params["before"] = ["{:d}".format(before)]
        if after is not None:
            params["after"] = ["{:d}".format(after)]
        if limit is not None:
            params["limit"] = ["{:d}".format(limit)]

        data = cls._handler.query(**params)
        return cls(data)


def parse_created_timestamp(created):
    created = datetime.strptime(created, "%a, %d %b. %Y %H:%M:%S")
    return created.replace(tzinfo=pytz.UTC)


class Events(ObjectSet, metaclass=EventsType):
    """MAAS event information."""

    __slots__ = "_prev_uri", "_next_uri"

    def __init__(self, eventmap):
        events = map(self._object, eventmap["events"])
        super(Events, self).__init__(events)
        self._prev_uri = eventmap["prev_uri"]
        self._next_uri = eventmap["next_uri"]

    @classmethod
    def _fetch(cls, uri, count):
        query = urlparse(uri).query
        params = parse_qs(query, errors="strict")
        if count is not None:
            params["limit"] = ["{:d}".format(count)]
        data = cls._handler.query(**params)
        return cls(data)

    def prev(self, count=None):
        """Load the previous (older) page/batch of events.

        :param count: A limit on the number of events to fetch. By default the
            limit is the same as that specified for this set of events.
        """
        if self._prev_uri is None:
            return self[:0]  # An empty slice of `self`.
        else:
            return self._fetch(self._prev_uri, count)

    def next(self, count=None):
        """Load the next (newer) page/batch of events.

        :param count: A limit on the number of events to fetch. By default the
            limit is the same as that specified for this set of events.
        """
        if self._next_uri is None:
            return self[:0]  # An empty slice of `self`.
        else:
            return self._fetch(self._next_uri, count)

    def backwards(self):
        """Iterate continuously through events, backwards.

        This will load new pages/batches of events on demand.
        """
        current = self
        while len(current) != 0:
            yield from current
            current = current.prev()

    def forwards(self):
        """Iterate continuously through events, forwards.

        This will load new pages/batches of events on demand.
        """
        current = self
        while len(current) != 0:
            yield from reversed(current)
            current = current.next()


def truncate(length, text):  # TODO: Move into utils.
    """Truncate the given text to the given length.

    If the text is longer than the ``length``, return a new string that
    contains ``length - 1`` characters of text followed by an ellipsis.
    Otherwise return the given text unaltered.
    """
    if len(text) > length:
        return text[:length - 1] + "…"
    else:
        return text


class Event(Object):
    """An event."""

    event_id = ObjectField(
        "id", readonly=True)
    event_type = ObjectField(
        "type", readonly=True)

    system_id = ObjectField(
        "node", readonly=True)
    hostname = ObjectField(
        "hostname", readonly=True)

    level = ObjectField.Checked(
        "level", Level.normalise, readonly=True)
    created = ObjectField.Checked(
        "created", parse_created_timestamp, readonly=True)

    description = ObjectField(
        "description", readonly=True)
    description_short = ObjectField.Checked(
        "description", partial(truncate, 50), readonly=True)

    def __repr__(self):
        return (
            "<{self.__class__.__name__} {self.created:%Y-%m-%d %H:%M:%S} "
            "{self.level.name} {self.hostname} {self.description_short!r}>"
        ).format(self=self)
