# Phenom CRM Automation

This project uses Playwright with pytest and a page-object architecture.

- `pages/` contains business actions and page objects.
- `utils/` contains reusable browser and framework helpers.
- `tests/` contains test cases and shared fixtures.
- `resources/` contains test data and locator definitions.
- `config/` contains non-secret configuration defaults.

Credentials are loaded from the ignored `.env` file. Install dependencies with
`pip install -r requirements.txt` before running the test suite.

## Architectural Principles

Business actions belong in page classes, reusable browser interactions belong
in utility or base classes, and assertions should remain in test cases wherever
practical. This separation keeps the framework easy to extend for negative and
edge-case scenarios.

- `interview_page.py` handles scheduling, rescheduling, and cancellation.
- `activity_page.py` verifies activity and communication history.
- `base_page.py` provides common interactions such as clicking, filling,
  waiting, scrolling, and refreshing.
- `conftest.py` provides browser and page fixtures.
