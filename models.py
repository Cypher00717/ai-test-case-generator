from typing import Literal
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    id: str
    title: str
    type: Literal["Positive", "Negative", "Edge"]
    priority: Literal["High", "Medium", "Low"]
    preconditions: list[str]
    steps: list[str]
    expected_result: str


class TestCaseResponse(BaseModel):
    __test__ = False

    test_cases: list[TestCase] = Field(min_length=1, description="A list of generated test cases. Must contain at least one test case.")


class GroundingFinding(BaseModel):
    test_case_id: str
    status: Literal[
        "Supported",
        "Unsupported",
        "Needs clarification",
    ]
    explanation: str


class GroundingEvaluation(BaseModel):
    __test__ = False

    findings: list[GroundingFinding] = Field(min_length=1)



class CoverageFinding(BaseModel):
    scenario: str
    importance: Literal["High", "Medium", "Low"]
    reason: str


class CoverageEvaluation(BaseModel):
    __test__ = False

    irrelevant_test_cases: list[dict]
    missing_required_scenarios: list[CoverageFinding]
    suggested_additional_scenarios: list[CoverageFinding]
