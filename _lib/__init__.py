import argparse
import os.path
import sys


# matplotlib defaults:
MP_DEFAULT_DPI = 100
MP_DEFAULT_FIGURE_WIDTH_INCHES = 6.4
MP_DEFAULT_FIGURE_HEIGHT_INCHES = 4.8


def _progname():
    return os.path.basename(sys.argv[0])


_DEFAULT_ARGSPEC = {
    ("input",): {
        "nargs": "*",
        "help": ("Paths to input files in parse-saa format.  Read from stdin "
                 "if no arguments are supplied."),
    },
    ("-o", "--output"): {
        "metavar": "PATH",
        "default": f"{_progname()}.png",
        "help": "Path to output file.",
    },
    ("--doctest",): {
        "action": "store_true",
        "help": "Run doctests.",
    },
    ("-v", "--verbose"): {
        "action": "store_true",
        "help": "Run verbosely.",
    },
    ("--dpi",): {
        "type": int,
        "default": MP_DEFAULT_DPI,
        "help": ("matplotlib dots per square inch.  See "
                 "https://stackoverflow.com/a/47639545 for a visual "
                 "demonstration of how this value impacts output."),
    },
    ("--figsize-width-inches",): {
        "type": float,
        "metavar": "INCHES",
        "default": MP_DEFAULT_FIGURE_WIDTH_INCHES,
        "help": "matplotlib figure width in inches.  See also: --dpi.",
    },
    ("--figsize-height-inches",): {
        "type": float,
        "metavar": "INCHES",
        "default": MP_DEFAULT_FIGURE_WIDTH_INCHES / 2,
        "help": "matplotlib figure height in inches.  See also: --dpi.",
    },
}


def merge_argspec(overlay=None, base=None):
    merged = base
    if not merged:
        merged = _DEFAULT_ARGSPEC.copy()
    if not overlay:
        return merged
    for k, v in overlay.items():
        if k in merged:
            if v:
                merged[k].update(v)
            else:
                del merged[k]
        else:
            if v:
                merged[k] = v
    return merged


def parse_args(argv=None, argspec=None):
    if not argv:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    argspec = merge_argspec(argspec)
    for k, v in argspec.items():
        parser.add_argument(*k, **v)

    args = parser.parse_args(argv[1:])

    if getattr(args, "doctest", False):
        # pylint: disable=import-outside-toplevel
        import doctest
        failures, _ = doctest.testmod(verbose=getattr(args, "verbose", False))
        if failures:
            raise Exception(f"{failures} doctest failures")
        sys.exit(0)

    return args
