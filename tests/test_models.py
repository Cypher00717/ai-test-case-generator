import pytest
from pydantic import ValidationError

from models import TestCaseResponse


VALID_RESPONSE = {
    "test_cases": [
        {
            "id": "TC-001",
            "title": "Reset password with registered email",
            "type": "Positive",
            "priority": "High",
            "preconditions": ["User has a registered email"],
            "steps": ["Enter registered email", "Submit request"],
            "expected_result": "A reset link is sent"
        }
    ]
}


def test_valid_response_passes():
    result = TestCaseResponse.model_validate(VALID_RESPONSE)

    assert len(result.test_cases) == 1
    assert result.test_cases[0].id == "TC-001"


def test_invalid_priority_fails():
    data = VALID_RESPONSE.copy()
    data["test_cases"] = [
        {**VALID_RESPONSE["test_cases"][0], "priority": "Critical"}
    ]

    with pytest.raises(ValidationError):
        TestCaseResponse.model_validate(data)


def test_missing_required_field_fails():
    test_case = {
        key: value
        for key, value in VALID_RESPONSE["test_cases"][0].items()
        if key != "expected_result"
    }

    data = {"test_cases": [test_case]}

    with pytest.raises(ValidationError):
        TestCaseResponse.model_validate(data)


def test_empty_test_case_list_fails():
    with pytest.raises(ValidationError):
        TestCaseResponse.model_validate({"test_cases": []})
