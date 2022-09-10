import collections
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


def merge_adjoining(it, closeness=datetime.timedelta(hours=4)):
    """Merge adjoining events from iterator it.

    Two events, a and b, are adjoining if b starts when a ends.
    Iterator it must yield events in ascending chronological order.
    """
    # How do adjoining events occur in the dataset?
    # I suspect they are an artefact of the following real-world pattern:
    #
    #   An alarm is set to activate after ~8h of sleep.
    #   I go to sleep.
    #   ~8h later, the alarm activates, and is dismissed.  (No snooze.)
    #   -> The first event is recorded.
    #   I sleep some more. :)
    #   Later, after waking naturally without an alarm,
    #   I add a new sleep event to record the additional time spent asleep.
    #   -> The second event is recorded.
    #
    # Such events are almost always perfectly adjoining.
    # The first event ends on the same minute the next event starts.
    #
    # Events are not always perfectly adjoining -- for reasons unknown.
    # We merge an event with its preceding event if they are only separated by
    # a small number of hours.  closeness defines the merge threshold.

    adj = collections.deque()
    for next_event in it:
        if not adj:
            adj.append(next_event)
            continue

        last_event = adj[-1]
        if next_event.since - last_event.until <= closeness:
            adj.append(next_event)
            continue

        # last_event not adjacent to next_event; flush
        yield Event(since=adj[0].since, until=adj[-1].until)
        adj.clear()
        adj.append(next_event)
        continue

    if adj:
        yield Event(since=adj[0].since, until=adj[-1].until)
        adj.clear()


if __name__ == "__main__":
    ltesting.main()
