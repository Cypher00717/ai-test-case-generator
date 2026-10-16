from dotenv import load_dotenv
from google import genai
import os

from generate_tests import generate_test_cases
from evaluator import evaluate_grounding, evaluate_coverage, find_duplicate_candidates

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.5-flash-lite"

requirement = """
Users should be able to reset their password using their
registered email address.
A password reset link should be sent to the registered email.
The link should allow the user to set a new password.
"""

# Generate and validate test cases
test_cases = generate_test_cases(requirement)

# Evaluate whether the cases are grounded in the requirement
result = evaluate_grounding(
    requirement=requirement,
    response=test_cases,
    client=client,
    model=MODEL,
)

print(result, response := test_cases.model_dump(), sep="\n\n")


# Evaluate coverage of the requirement by the test cases
coverage = evaluate_coverage(
    requirement=requirement,
    response=test_cases,
    client=client,
    model=MODEL,
)

print("\nCoverage evaluation:")
print(coverage)


# Find duplicate test case candidates
duplicates = find_duplicate_candidates(test_cases)

print("\nDuplicate candidates:")
print(duplicates)