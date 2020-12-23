import collections

from _lib import ltesting


def nextnr(it, n=2):
    """Yield n-many successive items from an iterator as a list, rotating by one
    element on each call.

    >>> import itertools
    >>> it = itertools.count()
    >>> next(it)
    0
    >>> next(it)
    1
    >>> rit = nextnr(it)
    >>> next(rit)
    [2, 3]
    >>> next(rit)
    [3, 4]

    """
    buf = collections.deque(maxlen=n)
    while True:
        try:
            e = next(it)
        except StopIteration:
            if buf:
                yield list(buf)
            return
        buf.append(e)
        if len(buf) < n:
            continue
        yield list(buf)


if __name__ == "__main__":
    ltesting.main()
