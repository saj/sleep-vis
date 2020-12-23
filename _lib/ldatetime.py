import calendar
import datetime
import typing

from _lib import ltesting
from _lib.litertools import nextnr


DEFAULT_CELL_WIDTH_MINUTES = 60

_MINUTES_IN_DAY = 24 * 60


class Period(typing.NamedTuple):
    # pylint: disable=inherit-non-class
    # pylint: disable=too-few-public-methods

    since: datetime.datetime
    until: datetime.datetime

    @property
    def duration(self):
        return self.until - self.since

    @property
    def duration_seconds(self):
        return self.duration.total_seconds()

    def intersectedness(self, other):
        """Return a number between 0 and 1 (inclusive) that indicates to what
        degree this Period is intersected by another.

        Returns 0 when this Period does not intersect with other.

        >>> parse = datetime.datetime.fromisoformat
        >>> p = Period(since=parse("2020-12-19 02:00:00"),
        ...            until=parse("2020-12-19 02:30:00"))
        >>> o = Period(since=parse("2020-12-19 02:34:00"),
        ...            until=parse("2020-12-19 10:30:00"))
        >>> p.intersectedness(o)
        0

        Returns 1 when this Period is wholly intersected by other.

        >>> parse = datetime.datetime.fromisoformat
        >>> p = Period(since=parse("2020-12-19 03:00:00"),
        ...            until=parse("2020-12-19 03:30:00"))
        >>> o = Period(since=parse("2020-12-19 02:34:00"),
        ...            until=parse("2020-12-19 10:30:00"))
        >>> p.intersectedness(o)
        1

        Returns a value 0 < v < 1 when this Period is partially intersected by
        other.  The fraction scales linearly with the proportion of the
        intersected span in the base Period.

        >>> parse = datetime.datetime.fromisoformat
        >>> p = Period(since=parse("2020-12-15 11:30:00"),
        ...            until=parse("2020-12-15 12:00:00"))
        >>> o = Period(since=parse("2020-12-15 03:53:00"),
        ...            until=parse("2020-12-15 11:57:00"))
        >>> p.intersectedness(o)
        0.9

        """
        assert self.since <= self.until
        assert other.since <= other.until

        if other.until <= self.since:
            return 0
        if other.since >= self.until:
            return 0
        if other.since <= self.since and other.until >= self.until:
            return 1

        width = self.until - self.since
        if other.since <= self.since:
            overlap = other.until - self.since
        else:
            overlap = self.until - other.since
        return overlap.total_seconds() / width.total_seconds()


def coerce_date(d):
    """Coerce d to a datetime.date.

    Returns a copy of d if d is already of type datetime.date.

    >>> d1 = datetime.date(2017, 11, 7)
    >>> d2 = coerce_date(d1)
    >>> d1 == d2
    True
    >>> d1 is d2
    False

    Strips time data if d is of type datetime.datetime.

    >>> coerce_date(datetime.datetime(2017, 11, 7, 5, 52))
    datetime.date(2017, 11, 7)

    """
    try:
        return datetime.date(year=d.year, month=d.month, day=d.day)
    except AttributeError:
        pass
    raise ValueError(f"unable to coerce value to date: {d!r}")


def coerce_datetime(d):
    """Coerce d to a (possibly partial) datetime.datetime.

    Returns a copy of d if d is already of type datetime.datetime.

    >>> d1 = datetime.datetime(2017, 11, 7, 5, 52)
    >>> d2 = coerce_datetime(d1)
    >>> d1 == d2
    True
    >>> d1 is d2
    False

    Returns a partial datetime.datetime if d is of type datetime.date.

    >>> coerce_datetime(datetime.date(2017, 11, 7))
    datetime.datetime(2017, 11, 7, 0, 0)

    Parses common default datetime.datetime string representations.

    >>> coerce_datetime("2017-11-07 05:52")
    datetime.datetime(2017, 11, 7, 5, 52)
    >>> coerce_datetime("2017-11-07T05:52")
    datetime.datetime(2017, 11, 7, 5, 52)

    """
    coercions = [
        # pylint: disable=unnecessary-lambda
        lambda d: datetime.datetime(
            year=d.year, month=d.month, day=d.day, hour=d.hour, minute=d.minute,
            second=d.second, microsecond=d.microsecond, tzinfo=d.tzinfo,
            fold=d.fold),
        lambda d: datetime.datetime(year=d.year, month=d.month, day=d.day),
        lambda d: datetime.datetime.fromisoformat(d),
    ]
    for c in coercions:
        try:
            return c(d)
        except (AttributeError, ValueError):
            pass
    raise ValueError(f"unable to coerce value to datetime: {d!r}")


def cells(start, cell_width_minutes=DEFAULT_CELL_WIDTH_MINUTES):
    """Yield successive leading time cell boundaries as datetime objects
    starting at midnight on start, a date-like object.

    >>> it = cells(datetime.date(2020, 1, 7))
    >>> l = [next(it) for _ in range(50)]
    >>> str(l[0])
    '2020-01-07 00:00:00'
    >>> str(l[1])
    '2020-01-07 01:00:00'
    >>> str(l[23])
    '2020-01-07 23:00:00'
    >>> str(l[24])
    '2020-01-08 00:00:00'
    >>> str(l[25])
    '2020-01-08 01:00:00'

    start may also be a datetime; the time component is ignored.

    >>> dseq = cells(datetime.date(2020, 1, 7))
    >>> tseq = cells(datetime.datetime(2020, 1, 7, hour=14, minute=42))
    >>> all(next(dseq) == next(tseq) for _ in range(50))
    True

    cell_width_minutes must be a factor of 1,440, the notional number of minutes
    in one day.

    >>> cells(datetime.date(2020, 1, 7), cell_width_minutes=42)
    Traceback (most recent call last):
        ...
    ValueError: cell width 42 is not a factor of 1440

    """
    ncells = cells_in_day(cell_width_minutes)
    cw = datetime.timedelta(minutes=cell_width_minutes)
    dw = datetime.timedelta(days=1)

    def _seq():
        day = coerce_date(start)
        while True:
            dt = coerce_datetime(day)
            for i in range(ncells):
                yield dt + i * cw
            day += dw
    return _seq()


def cellsp(start, cell_width_minutes=DEFAULT_CELL_WIDTH_MINUTES):
    """Like cells, but yield successive Periods.

    >>> it = cellsp(datetime.date(2020, 1, 7))
    >>> p = next(it)
    >>> isinstance(p, Period)
    True
    >>> p.since
    datetime.datetime(2020, 1, 7, 0, 0)
    >>> p.until
    datetime.datetime(2020, 1, 7, 1, 0)

    """
    for bounds in nextnr(cells(start, cell_width_minutes)):
        yield Period(since=bounds[0], until=bounds[1])


def cells_in_day(cell_width_minutes=DEFAULT_CELL_WIDTH_MINUTES):
    if _MINUTES_IN_DAY % cell_width_minutes:
        raise ValueError(f"cell width {cell_width_minutes!r} is not a factor "
                         f"of {_MINUTES_IN_DAY}")
    return _MINUTES_IN_DAY // cell_width_minutes


def ymd(dt):
    """Return the (year, month, day) 3-tuple from a datetime value."""
    return dt.year, dt.month, dt.day


def weekday_idx(dt):
    """Return the weekday index for a datetime value.  0 is Monday."""
    return calendar.weekday(*ymd(dt))


def weekday_name(wdidx):
    """Return the abbreviated weekday name for a weekday index."""
    return calendar.day_abbr[wdidx]


def fmt_seconds_hhmm(s):
    """Format a positive duration s seconds as hh:mm.

    >>> fmt_seconds_hhmm(4500.48)
    '01:15'

    >>> fmt_seconds_hhmm(-3600)
    Traceback (most recent call last):
        ...
    ValueError: value is negative: -3600

    """
    if s < 0:
        raise ValueError(f"value is negative: {s!r}")
    s = int(s)
    h = s // (60 * 60)
    s -= h * 60 * 60
    m = s // 60
    return f"{h:02}:{m:02}"


def fmt_minutes_hhmm(m):
    """Format a positive duration m minutes as hh:mm.

    >>> fmt_minutes_hhmm(75.48)
    '01:15'

    """
    return fmt_seconds_hhmm(m * 60)


if __name__ == "__main__":
    ltesting.main()
