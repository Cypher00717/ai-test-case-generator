from models import TestCaseResponse

TestCaseResponse.model_validate({
    "test_cases": [
        {
            "id": "TC-001",
            "title": "Example test",
            "type": "Positive",
            "priority": "Critical",
            "preconditions": [],
            "steps": ["Execute action"],
            "expected_result": "Action succeeds"
        }
    ]
})