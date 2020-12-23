def main(argv=None):
    # pylint: disable=import-outside-toplevel
    import argparse
    import doctest
    import sys

    if not argv:
        argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--doctest", action="store_true",
                        help="Run doctests.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Run verbosely.")
    args = parser.parse_args(argv[1:])

    if args.doctest:
        failures, _ = doctest.testmod(verbose=args.verbose)
        if failures:
            raise Exception(f"{failures} doctest failures")
        sys.exit(0)

    raise Exception(f"{argv[0]} is not executable")
