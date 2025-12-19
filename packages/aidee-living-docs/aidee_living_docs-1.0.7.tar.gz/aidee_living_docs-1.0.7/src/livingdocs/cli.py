"""cli entry point for livingdocs.

Parse command line arguments, invoke proper methods.
"""

import argparse
import logging
import sys

from . import __version__


def main(args=None):
    """Entry point for aidee-living-docs cli.

    The .toml entry_point wraps this in sys.exit already so this effectively
    becomes sys.exit(main()).
    The __main__ entry point similarly wraps sys.exit().
    """
    if args is None:
        args = sys.argv[1:]

    parsed_args = __get_args(args)
    logging.basicConfig(
        level=getattr(logging, parsed_args.log_level.upper(), logging.INFO),
        format="%(asctime)s:%(levelname)s:%(message)s",
    )


def __get_args(args):
    """Parse arguments passed in from shell."""
    return __get_parser().parse_args(args)


def __get_parser():
    """Return ArgumentParser."""
    parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description="Aidee Living Documentation application",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    log_levels = ["CRITICAL", "WARNING", "INFO", "DEBUG"]
    parser.add_argument(
        "--log-level",
        help=f"Log level ({log_levels})",
        choices=log_levels,
        default="WARNING",
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Echo version number.",
        version=f"{__version__}",
    )
    return parser


if __name__ == "__main__":
    main()
