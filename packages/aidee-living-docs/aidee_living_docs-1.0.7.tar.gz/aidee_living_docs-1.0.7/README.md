# Aidee Living Documentation Helpers

[![PyPI](https://img.shields.io/pypi/v/aidee-living-docs.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/aidee-living-docs.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/aidee-living-docs)][python version]
[![License](https://img.shields.io/pypi/l/aidee-living-docs)][license]

[![Tests](https://github.com/aidee-health/aidee-living-docs/workflows/Tests/badge.svg)][tests]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/aidee-living-docs/
[status]: https://pypi.org/project/aidee-living-docs/
[python version]: https://pypi.org/project/aidee-living-docs
[tests]: https://github.com/aidee-health/aidee-living-docs/actions?workflow=Tests
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- Helper functions to generate living documentation with Sphinx and Behave
- Type safe code using [ty](https://docs.astral.sh/ty/) for type checking

## Requirements

- Python 3.9-3.11

## Installation

You can install _Aidee Living Documentation_ via [pip]:

```console
$ pip install aidee-living-docs
```

This adds `aidee-living-docs` as a library, but also provides the CLI application with the same name.

## Using the application from the command line

The application also provides a CLI application that is automatically added to the path when installing via pip.

Once installed with pip, type:

```
aidee-living-docs --help
```

To see which options are available.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

[file an issue]: https://github.com/aidee-health/aidee-living-docs/issues
[pip]: https://pip.pypa.io/

## Credits

This project has been heavily inspired by [Bluefruit](https://github.com/bluefruit/LivingDocumentationHelpers)

<!-- github-only -->

[license]: https://github.com/aidee-health/aidee-living-docs/blob/main/LICENSE
[contributor guide]: https://github.com/aidee-health/aidee-living-docs/blob/main/CONTRIBUTING.md
