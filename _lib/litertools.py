import collections

from _lib import ltesting


def nextnr(it, n=2):
    """Yield n-many successive items from an iterator as a tuple,
    rotating by one element on each call.

    >>> it = iter(range(5))
    >>> next(it)
    0
    >>> next(it)
    1
    >>> rit = nextnr(it)
    >>> next(rit)
    (2, 3)
    >>> next(rit)
    (3, 4)

    If the underlying iterator yields at least n-many elements,
    the first tuple from nextnr will always be an n-tuple:

    >>> it = iter(range(3))
    >>> rit = nextnr(it, n=3)
    >>> next(rit)
    (0, 1, 2)

    Trailing tuples will be of smaller length:

    >>> next(rit)
    (1, 2)
    >>> next(rit)
    (2,)
    >>> next(rit)
    Traceback (most recent call last):
      ...
    StopIteration

    nextnr may therefore be applied to iterators yielding fewer than n elements:

    >>> it = iter(range(3))
    >>> rit = nextnr(it, n=5)
    >>> next(rit)
    (0, 1, 2)
    >>> next(rit)
    (1, 2)
    >>> next(rit)
    (2,)
    >>> next(rit)
    Traceback (most recent call last):
      ...
    StopIteration

    """
    buf = collections.deque(maxlen=n)
    while True:
        try:
            e = next(it)
        except StopIteration:
            while buf:
                yield tuple(buf)
                buf.popleft()
            return
        buf.append(e)
        if len(buf) < n:
            continue
        yield tuple(buf)
        buf.popleft()


def nextnrfull(it, n=2):
    """Like nextnr, but never yields a tuple of length less than n.

    >>> it = iter(range(4))
    >>> rit = nextnrfull(it, n=3)
    >>> next(rit)
    (0, 1, 2)
    >>> next(rit)
    (1, 2, 3)
    >>> next(rit)
    Traceback (most recent call last):
      ...
    StopIteration

    """
    for tup in nextnr(it, n):
        if len(tup) < n:
            break
        yield tup


if __name__ == "__main__":
    ltesting.main()
