"""Implement Formatter functionality for Behave."""

import time
from itertools import chain

from behave.formatter.base import Formatter
from behave.model import Feature
from behave.model import Scenario
from behave.model import Step


class CollectedStep:
    """A BDD Step."""

    def __init__(
        self,
        name: str,
        step_type: str,
        text: list[str] | None = None,
        error_message: list[str] | None = None,
        status: str = "not run",
    ):
        self.name = name
        self.step_type = step_type
        self.text: list[str] = text if text else []
        self.error_message = error_message
        self.status = status

    @classmethod
    def from_json(cls, data):
        return cls(**data)


class CollectedScenario:
    """A BDD scenario."""

    def __init__(
        self,
        name: str,
        tags: list[str],
        status: str = "not run",
        steps: list[CollectedStep] | None = None,
    ):
        self.name = name
        self.tags: list[str] = tags
        self.status = status
        self.steps: list[CollectedStep] = [] if (steps is None) else steps

    @classmethod
    def from_json(cls, data):
        steps = list(map(CollectedStep.from_json, data["steps"]))
        data.pop("steps", None)
        return cls(steps=steps, **data)


class CollectedRule:
    """A BDD rule."""

    def __init__(
        self,
        name: str,
        description: list[str],
        tags: list[str],
        scenarios: list[CollectedScenario] | None = None,
    ):
        self.name = name
        self.description: list[str] = description
        self.tags: list[str] = tags
        self.scenarios: list[CollectedScenario] = scenarios if scenarios else []

    @classmethod
    def from_json(cls, data):
        scenarios = list(map(CollectedScenario.from_json, data["scenarios"]))
        data.pop("scenarios", None)
        return cls(scenarios=scenarios, **data)


class CollectedFeature:
    """A BDD Feature."""

    def __init__(
        self,
        file_name: str,
        name: str,
        description: list[str],
        tags: list[str],
        start_time: float | None = None,
        run_time: float = 0,
        scenarios: list[CollectedScenario] | None = None,
        rules: list[CollectedRule] | None = None,
    ):
        self.file_name = file_name
        self.name = name
        self.description: list[str] = description
        self.tags: list[str] = tags
        self.start_time = start_time if start_time else time.time()
        self.run_time = run_time
        self.scenarios: list[CollectedScenario] = [] if (scenarios is None) else scenarios
        self.rules: list[CollectedRule] = [] if (rules is None) else rules

    def finished(self):
        self.run_time = time.time() - self.start_time

    @classmethod
    def from_json(cls, data):
        scenarios = list(map(CollectedScenario.from_json, data["scenarios"]))
        data.pop("scenarios", None)
        rules = list(map(CollectedRule.from_json, data["rules"]))
        data.pop("rules", None)
        return cls(scenarios=scenarios, rules=rules, **data)


class CollectingFormatter(Formatter):
    """Formatter for collected scenarios, rules and features."""

    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)

        self.current_feature: CollectedFeature | None = None
        self.current_rule: CollectedRule | None = None
        self.current_scenario: CollectedScenario | None = None
        self.current_step: CollectedStep | None = None

        self.steps_to_process: list[CollectedStep] = []
        self.current_step_text: list[str] = []

    def write_function(self):
        def formatter_write_line(*values, sep=""):
            line = sep.join(map(str, chain.from_iterable(values)))
            print(line)
            self.current_step_text.append(line)

        return formatter_write_line

    def feature(self, feature: Feature):
        self.current_feature = CollectedFeature(feature.filename, feature.name, feature.description, feature.tags)

    def rule(self, rule):
        self.current_rule = CollectedRule(rule.name, rule.description, rule.tags)
        assert self.current_feature
        self.current_feature.rules.append(self.current_rule)

    def background(self, background):
        pass

    def scenario(self, scenario: Scenario):
        self.current_scenario = CollectedScenario(scenario.name, scenario.tags)
        if not self.current_rule:
            assert self.current_feature
            self.current_feature.scenarios.append(self.current_scenario)
        else:
            self.current_rule.scenarios.append(self.current_scenario)
        self.steps_to_process = []

    def step(self, step: Step):
        """Append step to scenario."""
        step_to_store = CollectedStep(step.name, step.keyword)
        assert self.current_scenario
        self.current_scenario.steps.append(step_to_store)

        self.steps_to_process.append(step_to_store)

    def match(self, match):
        """Match next step."""
        self.current_step = self.steps_to_process.pop(0)
        self.current_step_text = []

    def result(self, step):
        """Result."""
        assert self.current_step
        assert self.current_scenario
        self.current_step.status = step.status.name
        self.current_step.text = self.current_step_text
        self.current_step.error_message = step.error_message

        self.current_scenario.status = step.status.name

    def eof(self):
        """End of file reached."""
        assert self.current_feature
        self.current_feature.finished()
