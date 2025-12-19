"""Module for creating a BDD feature file."""

import json
import sys  # Import sys
from pathlib import Path  # Import Path

from .collecting_formatter import CollectedFeature


def load_feature_file(feature_path: str):
    """Load a BDD feature file."""
    if not Path(feature_path).exists():
        print("Unable to find feature file\\n")
        sys.exit(2)  # Use sys.exit

    with open(feature_path) as file:
        return CollectedFeature.from_json(json.load(file))


def load_all_feature_files_in_directory(featurespath: str):
    """Load all BDD feature files in directory."""
    files = Path(featurespath).glob("*.json")

    features = []
    for file_path_obj in files:
        file = str(file_path_obj)
        feature = load_feature_file(file)
        features.append(feature)

    return features


status_to_style_dict: dict[str, str] = {
    "not run": "notrun",
    # behave.model_core.Status
    "untested": "notrun",
    "skipped": "notrun",
    "passed": "passed",
    "failed": "failed",
    "undefined": "notimplemented",
    "executing": "notrun",
}


def status_to_style(status: str):
    """Get a status style based on status"""
    return status_to_style_dict.get(status, "failed")
