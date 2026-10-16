
from models import TestCaseResponse
from evaluator import find_duplicate_candidates


def make_response(titles):
    return TestCaseResponse.model_validate({
        "test_cases": [
            {
                "id": f"TC-{i:03}",
                "title": title,
                "type": "Positive",
                "priority": "High",
                "preconditions": [],
                "steps": ["Execute the scenario"],
                "expected_result": "Expected behavior occurs",
            }
            for i, title in enumerate(titles, start=1)
        ]
    })


def test_similar_titles_are_flagged():
    response = make_response([
        "Reset password using registered email",
        "Reset password using registered email address",
    ])

    result = find_duplicate_candidates(response)

    assert len(result) == 1
    assert result[0]["test_case_ids"] == ["TC-001", "TC-002"]


def test_different_titles_are_not_flagged():
    response = make_response([
        "Reset password using registered email",
        "Reset password using unregistered email",
    ])

    result = find_duplicate_candidates(response)

    assert result == []


def test_single_test_case_has_no_duplicates():
    response = make_response([
        "Reset password using registered email",
    ])

    assert find_duplicate_candidates(response) == []
