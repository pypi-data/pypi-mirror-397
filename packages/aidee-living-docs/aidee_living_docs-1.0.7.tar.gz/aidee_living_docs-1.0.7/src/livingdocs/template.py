"""Template module using jinja2."""

import pathlib

from jinja2 import Environment
from jinja2 import FileSystemLoader


current_directory = pathlib.Path(__file__).parent.resolve()
env = Environment(autoescape=True, loader=FileSystemLoader(current_directory, followlinks=True))


def convert_template(filename, context):
    """Convert json context to output format with jinja."""
    template = env.get_template(filename)
    return template.render(**context)
