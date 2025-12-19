"""Module for generating user needs page."""

import sys

from .template import convert_template
from .userneeds import load_userneeds_from_file


def main(args=None):
    """Load input csv file with user needs."""
    if args is None:
        args = sys.argv

    if len(args) != 3:
        print(f"Invalid command format, format is:\n {args[0]} <userneed text file> <userneeds sphinx file>\n")
        sys.exit(1)

    userneeds = load_userneeds_from_file(args[1])

    context = {"userneeds": userneeds}

    with open(args[2], "w") as file:
        file.write(convert_template("userneeds.jinja2", context))


if __name__ == "__main__":
    main()
