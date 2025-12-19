"""Parse and format user needs."""

import csv


EXPECTED_NUMBER_OF_USERNEED_COLUMNS = 2


def load_userneeds_from_file(filename):
    """Load and parse user needs."""
    userneeds = []
    with open(filename) as tsv:
        next(tsv)  # Skip the title row
        for line in csv.reader(tsv, dialect="excel-tab"):
            if len(line) != EXPECTED_NUMBER_OF_USERNEED_COLUMNS:
                continue
            userneeds.append({"id": line[0], "description": line[1]})
    with open(filename) as csv_file:
        next(csv_file)  # Skip the title row
        for line in csv.reader(csv_file, dialect="excel"):
            if len(line) != EXPECTED_NUMBER_OF_USERNEED_COLUMNS:
                continue
            userneeds.append({"id": line[0], "description": line[1]})
    return userneeds
