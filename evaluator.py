
from difflib import SequenceMatcher
from models import GroundingEvaluation

import json
from dotenv import load_dotenv

from models import TestCaseResponse, CoverageEvaluation


def normalize_title(title: str) -> str:
    """Normalize a title for basic similarity comparison."""
    return " ".join(title.lower().split())


def find_duplicate_candidates(
    response: TestCaseResponse,
    threshold: float = 0.80,
) -> list[dict]:
    """Return pairs of titles that may describe duplicate scenarios."""
    duplicates = []
    test_cases = response.test_cases

    for i in range(len(test_cases)):
        for j in range(i + 1, len(test_cases)):
            first = test_cases[i]
            second = test_cases[j]

            if describe_different_scenarios(first.title, second.title):
                continue

            title_a = normalize_title(first.title)
            title_b = normalize_title(second.title)

            similarity = SequenceMatcher(
                None, title_a, title_b
            ).ratio()

            if similarity >= threshold:
                duplicates.append({
                    "test_case_ids": [first.id, second.id],
                    "titles": [first.title, second.title],
                    "similarity": round(similarity, 2),
                })

    return duplicates



def describe_different_scenarios(title_a: str, title_b: str) -> bool:
    """Detect known terms that distinguish scenario meaning."""
    a = normalize_title(title_a)
    b = normalize_title(title_b)

    pairs = [
        ("registered email", "unregistered email"),
        ("valid email", "invalid email"),
        ("valid password", "invalid password"),
        ("successful", "unsuccessful"),
        ("expired", "unexpired"),
        ("enabled", "disabled"),
        ("existing user", "nonexistent user"),
    ]

    return any(
        (left in a and right in b)
        or (right in a and left in b)
        for left, right in pairs
    )






load_dotenv()

def evaluate_grounding(requirement, response, client, model):
    test_cases = response.model_dump()

    prompt = f"""
    You are an independent QA reviewer.

    Compare each generated test case against the original requirement.

    ORIGINAL REQUIREMENT:
    {requirement}

    GENERATED TEST CASES:
    {json.dumps(test_cases, indent=2)}

    For each test case, inspect its preconditions, steps, and expected result.

    Classify findings as:
    - Supported: directly supported by the requirement.
    - Unsupported: asserts a business rule or behavior not established
    by the requirement.
    - Needs clarification: the requirement is ambiguous.

    Do not label a reasonable test action as unsupported merely because
    it is not explicitly written word-for-word in the requirement.
    Focus on claims about required system behavior.

    Return valid JSON only, using this structure:

    {{
    "findings": [
        {{
        "test_case_id": "TC-001",
        "status": "Supported",
        "explanation": "Explain the evidence from the requirement."
        }}
    ]
    }}

    Important evaluation rules:

    1. A test scenario may be a reasonable QA suggestion even when
    its expected behavior is not explicitly specified.

    2. Evaluate the expected_result separately from the test scenario.

    3. Do not treat an input constraint as proof of the system's
    behavior when that constraint is violated.

    4. For example, if a requirement specifies a registered email,
    this does not establish what message or behavior occurs when
    an unregistered email is submitted.

    5. If a test case asserts a specific outcome that the requirement
    does not establish, classify it as Needs clarification.

    6. Base every judgment on the requirement's actual statements,
    not on what a typical application would usually do.

    Include one finding per test case. Do not invent evidence.
    """

    result = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        },
    )

    data = json.loads(result.text)

    evaluation = GroundingEvaluation.model_validate(data)

    expected_ids = {tc.id for tc in response.test_cases}
    actual_ids = [finding.test_case_id for finding in evaluation.findings]

    if set(actual_ids) != expected_ids or len(actual_ids) != len(expected_ids):
        raise ValueError(
            "Grounding evaluation must contain exactly one finding "
            "for each generated test case."
        )

    return evaluation


def evaluate_coverage(requirement, response, client, model):
    prompt = f"""
    You are an independent QA reviewer.

    ORIGINAL REQUIREMENT:
    {requirement}

    GENERATED TEST CASES:
    {json.dumps(response.model_dump(), indent=2)}

    Evaluate the generated test cases for relevance and completeness.

    Relevance:
    - Identify test cases unrelated to the requirement.
    - Explain why each identified case is irrelevant.
    - Do not flag a reasonable negative test merely because it tests
    an input not explicitly described in the requirement.

    For completeness evaluation, separate findings into:

    1. Missing required scenarios:
    Important behaviors explicitly stated or clearly required by
    the original requirement that have no corresponding test case.A scenario is a missing required scenario only when its behavior
    is explicitly stated or clearly required by the original requirement.
    Otherwise, put it under suggested_additional_scenarios.

    2. Suggested additional scenarios:
    Useful defensive, negative, boundary, or security tests whose
    expected behavior is not specified by the requirement.

    Do not classify a scenario as a required omission merely because
    it is common industry practice.

    For example, do not treat password-reset link expiration as a
    required omission unless the requirement specifies expiration.

    Return valid JSON only, using this structure:

    Return exactly these three top-level keys:
    irrelevant_test_cases,
    missing_required_scenarios,
    suggested_additional_scenarios.

    Do not use "missing_scenarios" or any alternative field names.
    Return empty arrays when there are no findings.

    {{
    "irrelevant_test_cases": [
        {{
        "test_case_id": "TC-001",
        "reason": "Explanation"
        }}
    ],
    "missing_required_scenarios": [
        {{
        "scenario": "Description of the missing required behavior",
        "importance": "High",
        "reason": "Why the requirement requires this scenario"
        }}
    ],
    "suggested_additional_scenarios": [
        {{
        "scenario": "Description of a useful additional test",
        "importance": "Medium",
        "reason": "Why this test may be useful"
        }}
    ]
    }}

    Use empty arrays when no issues are identified.
    """

    result = client.models.generate_content(
        model=model,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )

    data = json.loads(result.text)

    return CoverageEvaluation.model_validate(data)

