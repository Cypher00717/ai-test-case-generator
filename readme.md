# AI Test Case Generator

An LLM-assisted QA utility that converts software requirements into structured test cases and evaluates the generated output for grounding, relevance, completeness, and potential duplication.

Built with Python, Google Gemini, Pydantic, and Pytest as a practice and portfolio project exploring AI Quality Engineering.

## Overview

Traditional test case design relies on testers translating requirements into executable scenarios. LLMs can assist with this process, but generated test cases may contain unsupported assumptions, omit important scenarios, or duplicate existing coverage.

This project explores how an SDET can build validation and evaluation checks around an LLM-powered test generation workflow.

The objective is not simply to generate test cases, but to assess whether the generated output is structurally valid, relevant to the requirement, and sufficiently grounded in the available information.

## Key Features

- **LLM-based test generation:** Converts requirement text into structured test cases using Google Gemini.
- **Structured output validation:** Uses Pydantic to validate required fields, data types, and allowed values.
- **Grounding evaluation:** Uses an LLM-based judge to identify supported behavior, unsupported assumptions, and cases requiring clarification.
- **Relevance and coverage evaluation:** Identifies irrelevant test cases and potential gaps in scenario coverage.
- **Duplicate candidate detection:** Uses Python's `difflib.SequenceMatcher` to flag potentially similar test case titles.
- **Automated validation tests:** Uses Pytest to verify schema validation and evaluator contracts.

## Architecture

```text
Software Requirement
        |
        v
Gemini LLM
        |
        v
Structured Test Cases
        |
        v
Pydantic Validation
        |
        v
Duplicate Candidate Detection
        |
        v
Grounding Evaluation
        |
        v
Relevance and Coverage Evaluation
        |
        v
QA Evaluation Results
```

The workflow separates test case generation from quality evaluation. The generator produces candidate test cases, while validation and evaluation components inspect the output.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation and workflow orchestration |
| Google Gemini API | Test case generation and LLM-based evaluation |
| `google-genai` | Python SDK for Gemini API integration |
| Pydantic | Schema and data validation |
| Pytest | Automated testing |
| JSON | Structured model input and output |
| `python-dotenv` | Local environment variable configuration |
| `difflib` | Baseline title-similarity comparison |

## Generated Test Case Structure

Each generated test case contains:

- `id` — unique test case identifier
- `title` — descriptive scenario title
- `type` — Positive, Negative, or Edge
- `priority` — High, Medium, or Low
- `preconditions` — conditions required before execution
- `steps` — sequential test actions
- `expected_result` — expected observable outcome

Example:

```json
{
  "test_cases": [
    {
      "id": "TC-001",
      "title": "Password reset with registered email address",
      "type": "Positive",
      "priority": "High",
      "preconditions": [
        "The user has a registered email address"
      ],
      "steps": [
        "Navigate to the password reset page",
        "Enter the registered email address",
        "Submit the password reset request"
      ],
      "expected_result": "A password reset link is sent to the registered email address"
    }
  ]
}
```

## Quality Evaluation

### 1. Schema Validation

Pydantic validates the structure of the generated response, including required fields and allowed values.

This catches malformed or incomplete data, but it does not establish whether a test case is correct or complete.

### 2. Grounding Evaluation

An LLM-based evaluator compares generated test cases against the original requirement.

Each case receives one of three statuses:

- `Supported` — behavior supported by the requirement
- `Unsupported` — behavior asserted without sufficient evidence
- `Needs clarification` — expected behavior is ambiguous or unspecified

For example, a password-reset requirement may state that a reset link is sent to a registered email address without defining what happens when an unregistered address is submitted. The evaluator should identify the unspecified behavior rather than assume a particular response.

### 3. Relevance and Coverage Evaluation

The evaluator examines whether test cases relate to the requirement and identifies potential missing scenarios.

Coverage findings distinguish required scenarios from suggested additional tests. Security and defensive test ideas are not automatically treated as mandatory requirements when their expected behavior has not been specified.

### 4. Duplicate Candidate Detection

A Python-based comparison identifies test case titles with high textual similarity.

This is a lightweight baseline. Similar titles can describe different scenarios, and differently worded titles can describe the same scenario. Results therefore require review rather than automatic deletion.

## Project Structure

```text
ai-test-case-generator/
├── generate_tests.py
├── models.py
├── evaluator.py
├── run_evaluation.py
├── check_gemini.py
├── list_models.py
├── tests/
│   ├── test_models.py
│   ├── test_evaluator.py
│   └── test_coverage.py
├── .env
├── .gitignore
└── README.md
```

The test filenames above reflect the intended project organization; adjust them if your local repository uses different names.

## Getting Started

### Prerequisites

- Python 3.11 or later, with a compatible version of the project dependencies
- A Google Gemini API key
- Internet connectivity for API requests

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai-test-case-generator
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install google-genai pydantic pytest python-dotenv
```

### 4. Configure the API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Never commit your actual API key to GitHub.

Ensure `.gitignore` contains:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
*.pyc
```

### 5. Verify the Gemini connection

```bash
python check_gemini.py
```

### 6. Run the generator and evaluator

```bash
python run_evaluation.py
```

The workflow sends requests to Gemini for generation and evaluation. API availability, quota limits, model access, and pricing depend on your Google AI Studio project and the selected model.

### 7. Run automated tests

```bash
python -m pytest -v
```

The initial validation and evaluator-contract suite reached **10 passing tests** during development. Rerun the suite against the current repository before treating that number as the final verified result.

## Testing Strategy

The project uses Pytest to test deterministic validation behavior and evaluator output contracts independently of live LLM requests.

Examples include:

- Valid response passes schema validation.
- Invalid priority is rejected.
- Missing required fields are rejected.
- Empty test case collections are rejected.
- Similar titles are flagged as duplicate candidates.
- Distinct scenarios should not be flagged solely because they share common words.
- Invalid coverage output is rejected.
- Missing required coverage fields are rejected.
- Invalid importance values are rejected.

LLM-generated judgments are probabilistic and may vary between runs. Passing schema tests does not prove the semantic correctness of the evaluator.

## Limitations

This is a small practice and portfolio project, not a production-ready AI testing platform.

Current limitations include:

- LLM evaluations may incorrectly classify supported or unsupported behavior.
- Coverage findings depend on the quality of the original requirement and evaluation prompt.
- Title similarity is not equivalent to semantic duplicate detection.
- Test case IDs and ordering may change between generation runs.
- The project does not guarantee exhaustive test coverage.
- Document ingestion, OCR, RAG, vector databases, frontend development, and production deployment are outside the current scope.
- Live API calls depend on external service availability and quotas.

The evaluation output should be treated as decision support for a QA engineer, not as an authoritative replacement for requirements review.

## Future Improvements

Potential next steps, if justified by a specific need:

- Add a small, versioned benchmark of requirements and expected evaluation outcomes.
- Test evaluator accuracy against manually reviewed examples.
- Measure false positives and false negatives in duplicate detection.
- Add document input for PDF, DOCX, or TXT requirements.
- Integrate the workflow into a CI pipeline.

These are possible extensions, not prerequisites for the current MVP.

## Learning Outcomes

This project explores:

- Prompt design for structured test case generation
- LLM API integration using Python
- Schema validation with Pydantic
- Automated testing of AI-powered utilities
- Grounding, relevance, and coverage evaluation
- LLM-as-a-judge limitations
- Deterministic versus probabilistic quality checks
- Designing QA safeguards around non-deterministic AI output

## Project Status

**Practice / portfolio MVP — core workflow implemented; final regression and integration verification should be performed against the current repository.**

The project demonstrates hands-on exploration of AI-assisted test generation and evaluation. It does not represent production deployment or production AI quality engineering experience.

## Author

Abhishek

SDET | QA Automation | Exploring AI Quality Engineering
