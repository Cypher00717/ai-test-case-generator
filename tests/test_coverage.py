
import pytest
from pydantic import ValidationError

from models import CoverageEvaluation


def test_valid_coverage_response():
    data = {
        "irrelevant_test_cases": [],
        "missing_required_scenarios": [],
        "suggested_additional_scenarios": [
            {
                "scenario": "Test reset link expiration",
                "importance": "Medium",
                "reason": "Useful security test, not specified in the requirement."
            }
        ]
    }

    result = CoverageEvaluation.model_validate(data)

    assert result.missing_required_scenarios == []
    assert len(result.suggested_additional_scenarios) == 1


def test_missing_required_key_fails():
    data = {
        "irrelevant_test_cases": [],
        "suggested_additional_scenarios": []
    }

    with pytest.raises(ValidationError):
        CoverageEvaluation.model_validate(data)


def test_invalid_importance_fails():
    data = {
        "irrelevant_test_cases": [],
        "missing_required_scenarios": [
            {
                "scenario": "Example",
                "importance": "Critical",
                "reason": "Example reason"
            }
        ],
        "suggested_additional_scenarios": []
    }

    with pytest.raises(ValidationError):
        CoverageEvaluation.model_validate(data)
