"""Create Sphinx compatible feature page."""

import pathlib
import sys
from pathlib import Path  # Import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader

from .collecting_formatter import CollectedStep
from .feature_file import load_feature_file
from .feature_file import status_to_style


current_directory = pathlib.Path(__file__).parent.resolve()
env = Environment(autoescape=True, loader=FileSystemLoader(current_directory, followlinks=True))
template = env.get_template("feature.jinja2")


def screenshots_from_step(step: CollectedStep):
    """Step screenshot."""
    screenshots = []
    for line in step.text:
        line_text: str = line.strip()
        line_split = line_text.split("'")
        if len(line_split) == 3 and line_split[0] == "Save screenshot ":
            screenshots.append(line_split[1])
    return screenshots


def main(args=None):
    """Entry point when running as script."""
    if args is None:
        args = sys.argv

    if len(args) != 2:
        print(f"Invalid command format, format is:\n {args[0]} <json feature result>\n")
        sys.exit(1)

    feature = load_feature_file(args[1])

    context = {
        "feature": feature,
        "status_to_style": status_to_style,
        "screenshots_from_step": screenshots_from_step,
    }

    file_path = Path(args[1])
    file_name = file_path.stem + ".rst"

    with open(file_name, "w") as file:
        file.write(template.render(**context))


def process_files_in_current_directory():
    """Process files."""
    files = Path().glob("*.json")

    for file_path_obj in files:
        file = str(file_path_obj)
        print(f"Converting {file}")
        feature = load_feature_file(file)

        context = {
            "feature": feature,
            "status_to_style": status_to_style,
            "screenshots_from_step": screenshots_from_step,
        }

        file_stem = Path(file).stem
        file_name = file_stem + ".rst"

        with open(file_name, "w") as f:
            f.write(template.render(**context))


if __name__ == "__main__":
    """If invoked directly as script, relay to main() method."""
    main()
