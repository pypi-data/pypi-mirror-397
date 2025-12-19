"""Create traceability. Link scenarios with status to user needs."""

import sys

from .collecting_formatter import CollectedScenario
from .feature_file import load_all_feature_files_in_directory
from .feature_file import status_to_style
from .template import convert_template
from .userneeds import load_userneeds_from_file


def add_scenario_to_userneed(userneeds, user_need_id, scenario_id, scenario_name, result):
    """Add scenario to proper user need."""
    user_need_id = user_need_id.lower()
    for userneed in userneeds:
        if userneed["id"].lower() == user_need_id:
            userneed["scenarios"].append({"id": scenario_id, "name": scenario_name, "result": result})


def userneed_id_for_scenario(scenario: CollectedScenario):
    """Find user need (un_-prefixed) in scenario."""
    for tag in scenario.tags:
        if tag.lower().startswith("un_"):
            return tag.lower()

    return ""


def id_for_scenario(scenario: CollectedScenario):
    """Find id tag for scenario (starting with id_)."""
    for tag in scenario.tags:
        if tag.lower().startswith("id_"):
            return tag

    return ""


def main(args=None):
    """Script entry point."""
    if args is None:
        args = sys.argv

    if len(args) != 4:
        print(
            f"Invalid command format, format is:\n {args[0]} <userneed text file> "
            "<path to feature file results> <output file>\n"
        )
        sys.exit(1)

    userneeds = load_userneeds_from_file(args[1])
    for userneed in userneeds:
        userneed["scenarios"] = []

    features = load_all_feature_files_in_directory(args[2])
    for feature in features:
        for scenario in feature.scenarios:
            user_need_id = userneed_id_for_scenario(scenario)
            scenario_id = id_for_scenario(scenario)
            result = scenario.status
            if user_need_id != "" and scenario_id != "":
                add_scenario_to_userneed(
                    userneeds,
                    user_need_id,
                    scenario_id,
                    feature.name + " - " + scenario.name,
                    result,
                )

    context = {"userneeds": userneeds, "status_to_style": status_to_style}

    with open(args[3], "w") as file:
        file.write(convert_template("userneeds_trace.jinja2", context))


if __name__ == "__main__":
    """Relay to main method when invoked as standalone script."""
    main()
