import datetime
import json
import typing

from _lib import ldatetime
from _lib import ltesting


PARSE_SAA_TIME_FORMAT = "%Y-%m-%dT%H:%M"


class Event(typing.NamedTuple):
    # pylint: disable=inherit-non-class
    # pylint: disable=too-few-public-methods

    since: datetime.datetime
    until: datetime.datetime

    def period(self):
        return ldatetime.Period(since=self.since, until=self.until)


def parse_events(file):
    """Return an iterator that lazily parses Event objects from file.

    Args:
        file: An open file object whose contents adhere to the specification
            documented in parse-saa.
    """
    for line in file:
        obj = json.loads(line)
        yield Event(parse_datetime(obj["since"]),
                    parse_datetime(obj["until"]))


def parse_datetime(stamp):
    """Return a datetime.datetime object parsed from a parse-saa time stamp.

    >>> parse_datetime("2017-11-07T05:52")
    datetime.datetime(2017, 11, 7, 5, 52)

    Raises ValueError if stamp is not in parse-saa format.

    >>> parse_datetime("2017-11-07 05:52")
    Traceback (most recent call last):
        ...
    ValueError: time data '2017-11-07 05:52' does not match format '%Y-%m-%dT%H:%M'

    """
    return datetime.datetime.strptime(stamp, PARSE_SAA_TIME_FORMAT)


if __name__ == "__main__":
    ltesting.main()
