import json
import os
from typing import Callable, Optional

from eocdb.core.models.qc_info import QC_INFO_STATUS_WAITING
from eocdb.core.val._meta_field_compare_rule import MetaFieldCompareRule
from eocdb.core.val._meta_field_optional_rule import MetaFieldOptionalRule
from eocdb.core.val._meta_field_required_rule import MetaFieldRequiredRule
from eocdb.ws.context import Config
from ..models.dataset import Dataset
from ..models.dataset_validation_result import DatasetValidationResult
from ..models.issue import Issue, ISSUE_TYPE_WARNING, ISSUE_TYPE_ERROR


validator_inst = None


def validate_dataset(dataset: Dataset, config: Config) -> DatasetValidationResult:
    global validator_inst
    if validator_inst is None:
        validator_inst = Validator()

    if "mock_validation" in config:
        return DatasetValidationResult("OK", [])

    return validator_inst.validate_dataset(dataset)


class Validator():

    def __init__(self):
        file = os.path.join(os.path.dirname(__file__), "res", "validation_config.json")

        with open(file) as f:
            rules_config = json.load(f)

        self._parse_rules(rules_config)

    def validate_dataset(self, dataset: Dataset) -> DatasetValidationResult:
        issues = []
        num_errors = 0
        for rule in self._header_rules:
            issue = rule.eval(dataset)
            if issue:
                issues.append(issue)
                if issue.type == ISSUE_TYPE_ERROR:
                    num_errors += 1

        status = "OK" if not issues else ISSUE_TYPE_ERROR if num_errors else ISSUE_TYPE_WARNING
        validation_result = DatasetValidationResult(status, issues)
        return validation_result

    def _parse_rules(self, rules_config):
        self._header_rules = []

        header_rules = rules_config["header"]
        for header_rule in header_rules:
            rule_type = header_rule["type"]
            if "field_compare" == rule_type:
                rule = self._create_meta_field_compare_rule(header_rule)
                self._header_rules.append(rule)
            elif "field_required" == rule_type:
                name = header_rule["name"]
                error = header_rule["error"]
                rule = MetaFieldRequiredRule(name, error)
                self._header_rules.append(rule)
            elif "field_optional" == rule_type:
                name = header_rule["name"]
                warning = header_rule["warning"]
                rule = MetaFieldOptionalRule(name, warning)
                self._header_rules.append(rule)
            else:
                raise ValueError("Invalid type of validation rule: " + rule_type)

    def _create_meta_field_compare_rule(self, header_rule):
        reference = header_rule["reference"]
        compare = header_rule["compare"]
        operation = header_rule["operation"]
        if "error" in header_rule:
            error = header_rule["error"]
        else:
            error = None
        if "warning" in header_rule:
            warning = header_rule["warning"]
        else:
            warning = None
        rule = MetaFieldCompareRule(reference, compare, operation, error=error, warning=warning)
        return rule
