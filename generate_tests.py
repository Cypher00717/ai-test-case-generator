import os

from dotenv import load_dotenv
from google import genai
from models import TestCaseResponse
import json

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_test_cases(requirement: str):
    prompt = f"""
    You are an experienced Software QA Engineer specializing in functional testing, negative testing, boundary testing, and test scenario design.

    Your task is to analyze the software requirement provided below and generate a set of relevant test cases.

    ## Instructions

    1. Understand the requirement and identify its explicitly stated functionality and business rules.
    2. Generate relevant positive, negative, and edge-case test scenarios wherever applicable.
    3. Cover the important behaviors described in the requirement without generating unnecessary or repetitive test cases.
    4. Each test case must verify a specific behavior and have a clear, observable expected result.
    5. Do not invent APIs, database fields, UI elements, workflows, business rules, validation rules, or system behavior that are not supported by the requirement.
    6. If a scenario depends on an unspecified business rule, do not present that rule as an established fact. Exclude the scenario or clearly identify the assumption in the test case.
    7. Do not claim that a particular implementation detail exists unless the requirement explicitly establishes it.
    8. Assign priority based on the requirement's stated functionality and the potential impact of failure. Do not mark every test case as High priority.
    9. Avoid duplicate test cases that verify essentially the same behavior.
    10. Use concise, actionable steps that a tester could follow.

    ## Required Output

    Return a JSON object containing a top-level `test_cases` array.

    Each test case must contain the following fields:

    - `id`: Unique test case identifier, using the format TC-001, TC-002, and so on.
    - `title`: Short, descriptive test case title.
    - `type`: One of Positive, Negative, or Edge.
    - `priority`: One of High, Medium, or Low.
    - `preconditions`: An array of preconditions required to execute the test.
    - `steps`: An array of sequential test execution steps.
    - `expected_result`: A clear, observable outcome that should occur if the system behaves as specified.

    ## Output Constraints

    - Return valid JSON only.
    - Do not include Markdown code fences, introductory text, or explanations outside the JSON object.
    - Include all required fields for every test case.
    - Use the specified field names and allowed values consistently.
    - Do not add extra fields.
    - If the requirement is ambiguous or insufficient to support a particular scenario, do not silently invent missing details.

    ## Software Requirement

    {requirement}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    raw_output = response.text
    data = json.loads(raw_output)
    validated_response = TestCaseResponse.model_validate(data)

    return validated_response


if __name__ == "__main__":
    requirement = """
    Users should be able to reset their password using their
    registered email address.
    A password reset link should be sent to the registered email.
    The link should allow the user to set a new password.
    """

    result = generate_test_cases(requirement)
    print(
    json.dumps(
        result.model_dump(),
        indent=2
    )
)