# Sporty QA Assessment — Test Plan, Defects and Automation

This repository contains the QA assessment for a sports-betting web application. It includes manual test planning, exploratory testing, defect documentation, and two automated application tests.

**Application under test:** https://qae-assignment-tau.vercel.app

## 1. Project Overview

The objective is to validate the single pre-match football betting journey and identify functional and business-rule defects.

| File / directory | Purpose |
|---|---|
| `test-plan.md` | Test scope, approach, assumptions, and six prioritized scenarios |
| `bug-report.md` | Documented defects with severity, reproduction steps, expected and actual results, and business impact |
| `evidence/` | Screenshots associated with the manual defect reports |
| `strategy-and-recommendations.md` | Rationale for automation selection, manual-only coverage, and recommendations |
| `automation/` | Python automation framework, automated tests, and generated test artifacts |

### Automated application tests

The assessment requires two automated tests: one UI test and one API test.

| Test | Type | File | Purpose |
|---|---|---|---|
| TC-01 — Single Bet Placement | UI | `automation/tests/ui/test_single_bet.py` | Validates the single-bet journey, including date filtering, selection, bet slip, stake, payout, receipt, and balance |
| TC-06 — Insufficient Balance Validation | API | `automation/tests/api/test_insufficient_balance.py` | Validates that an unaffordable bet is rejected and the balance remains unchanged |


## 2. Technology Stack

- **Python 3.11 or newer:** programming language.
- **pytest:** test runner, fixtures, assertions, and reporting.
- **Selenium:** browser automation for the UI test.
- **Google Chrome:** browser used by the UI test.
- **requests:** sends HTTP requests to the application's API.
- **Ruff:** Python linting and formatting.
- **Page Object Model (POM):** separates page interactions and reusable UI components from test assertions.


## 3. Prerequisites

Install the following before setting up the project:

1. Git
2. Python 3.11 or newer
3. Google Chrome (required for UI testing)
4. An internet connection or approved package index for installing dependencies
5. Network access for Selenium Manager to obtain a compatible ChromeDriver when necessary

### macOS: Install Homebrew and Python 3.11

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the installer's prompts and any printed instructions for adding `brew` to your PATH. Then install and verify Python:

```bash
brew install python@3.11
python3.11 --version
```

Alternatively, download the compatible macOS `.pkg` installer from the official Python release page, run it, and verify with `python3.11 --version`.

Official downloads: https://www.python.org/downloads/

For Python 3.11, use the official release page:

https://www.python.org/downloads/release/python-31117/

Choose the installer appropriate for your operating system.

### Windows

1. Download the Python 3.11 installer from the official Python website.
```powershell
py -3.11 --version
```

### Linux

Install Python 3.11 and its virtual-environment support using your Linux distribution's package manager or approved installation method.

Verify the installation:

```bash
python3.11 --version
```

Official documentation:

- macOS: https://docs.python.org/3.11/using/mac.html
- Windows: https://docs.python.org/3.11/using/windows.html
- General installation guidance: https://docs.python.org/3.11/using/

If the version command fails, resolve the Python installation or PATH issue before proceeding.

## 4. Clone the Repository

Open the [sporty-qae-assessment repository](https://github.com/coljyothsna-creator/sporty-qae-assessment) in your browser, or open a terminal in VS Code or your preferred terminal application and clone it:

```bash
git clone https://github.com/coljyothsna-creator/sporty-qae-assessment.git
cd sporty-qae-assessment
```

The project keeps its Python package configuration and tests inside the `automation/` directory. Move into that directory before executing the remaining commands:

```bash
cd automation
```

**Important:** Run the setup, installation, and test commands in this README from the `automation/` directory unless otherwise stated.

## 5. Create and Activate a Virtual Environment

A virtual environment isolates the dependencies required by this project. Create it once for your local checkout, then activate it whenever you start a new terminal session for testing.

### Step 1 — Create the environment

**macOS / Linux**

```bash
python3.11 -m venv .venv
```

**Windows**

```powershell
py -3.11 -m venv .venv
```

This creates a `.venv/` directory inside `automation/`.

### Step 2 — Activate the environment

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows — PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows — Command Prompt**

```cmd
.venv\Scripts\activate.bat
```

When activation succeeds, the terminal prompt normally displays `(.venv)`.

### Step 3 — Verify the environment

```bash
python --version
python -m pip --version
```

The Python version should be 3.11 or newer, and pip should point to the active virtual environment.

If activation fails, consult the troubleshooting section below.

## 6. Install Project Dependencies

**Do this after activating the virtual environment.**

First, upgrade pip:

```bash
python -m pip install --upgrade pip
```

Then install the project and its development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run these commands from the `automation/` directory, where `pyproject.toml` is located.

### What gets installed?

The dependency definitions are maintained in `automation/pyproject.toml`.

| Package | Purpose |
|---|---|
| `pytest` | Runs tests and produces test results |
| `selenium` | Controls the Chrome browser for UI automation |
| `requests` | Makes HTTP requests for API testing |
| `ruff` | Checks Python code style and formatting; included in the development dependencies |

The installation command reads the project's declared dependencies and installs compatible versions. You do not need to install these packages individually.

The project currently does not provide a complete dependency lock file, so exact transitive package versions may vary between installations.

### Verify the dependencies

```bash
python -m pytest --version
python -m pip show selenium
python -m pip show requests
python -m ruff --version
```

If these commands work, the relevant packages are installed in your active environment.

## 7. Configure the Test User

The application tests accept a user context through the `--user-id` option.

Use a valid, provisioned test account. Arbitrary generated IDs may be rejected as unauthorized.

For example, the following uses a placeholder:

```bash
python -m pytest -m "ui or api" --user-id <your-user-id>
```

Replace `<your-user-id>` with the actual test user ID. Do not type the angle brackets.

The UI test uses the user context in the application URL. The API client sends the corresponding context through the `x-user-id` header.

**Account safety:** bets can change the account balance. Use a dedicated test account rather than an account shared with manual testing or other users. The framework does not automatically reset the account balance.

## 8. Run the Tests

Run these commands from `automation/` with `.venv` activated.

### Run the UI test

```bash
python -m pytest tests/ui/test_single_bet.py --user-id <your-user-id>
```

To watch Chrome while the test runs:

```bash
python -m pytest tests/ui/test_single_bet.py --user-id <your-user-id> --headed
```

Chrome runs headless by default, without displaying its window. Add `--headed` to the UI test command above to see the browser window.

### Run the API test

```bash
python -m pytest tests/api/test_insufficient_balance.py --user-id <your-user-id>
```

The API test sends requests directly to the backend and does not launch Chrome.

The test requires a suitable starting balance: at least €1.01 and below €100.00. It does not reset the account balance.

### Run both required application tests

```bash
python -m pytest -m "ui or api" --user-id <your-user-id>
```

### Run all collected tests

```bash
python -m pytest
```

This currently collects the UI and API tests listed above. It may launch Chrome and access the application, and the UI test may place a bet.

For normal assessment execution, prefer the targeted commands above so the intended test scope is clear.

## 9. Test Options

| Option | Purpose | Default |
|---|---|---|
| `--user-id` | Supplies the test user's context | NA |
| `--base-url` | Overrides the application base URL | Configured application URL |
| `--ui-timeout` | Sets the UI timeout in seconds | 10 |
| `--api-timeout` | Sets the API timeout in seconds | 10 |
| `--headed` | Displays the Chrome window | Disabled; headless Chrome |

Example with a visible browser and a custom timeout:

```bash
python -m pytest -m ui --user-id <your-user-id> --headed --ui-timeout 15
```

## 10. Test Reports and Failure Evidence

The framework provides terminal results, INFO-level logs, optional JUnit XML output, and automatic screenshots for eligible UI failures.

### A. Terminal results and logs

pytest prints test outcomes and failure details in the terminal.

Review the complete output for:

- The test that failed
- The assertion or exception that caused the failure
- Expected and actual values, where reported
- Logged diagnostics and any screenshot path

The UI test collects multiple validation mismatches into its failure message, so a single failed test may report several inconsistencies.

### B. Automatic UI failure screenshots

When a UI test fails during setup or execution and a WebDriver is available, the framework attempts to capture a screenshot.

**Location:**

```text
automation/artifacts/screenshots/
```

To find the relevant screenshot:

1. Run the UI test.
2. Find the `Failure screenshot:` message in the terminal logs or the `Screenshot` section in the failure output.
3. Open the named PNG file under `automation/artifacts/screenshots/`.
4. Inspect the captured browser state.

The screenshot filename includes the test identifier and a unique suffix. The exact name changes between runs.

Screenshots can help investigate missing elements, unexpected UI states, incorrect receipt values, and balance inconsistencies.

**Limitations:**

- Screenshots are attempted for UI setup and test-call failures when a browser driver is available.
- API and unit test failures do not automatically produce browser screenshots.
- If screenshot capture fails, the capture error is logged without replacing the original test failure.
- Screenshots are stored as separate files; they are not embedded in the JUnit XML report.

### C. Generate a JUnit XML/HTML report

To generate a machine-readable report for the two required application tests:

```bash
python -m pytest -m "ui or api" --user-id <your-user-id> --junitxml=artifacts/results.xml
```

The report is saved to:

```text
automation/artifacts/results.xml
```

JUnit XML contains test-result and failure information suitable for CI systems. It is not a visual HTML report.

No HTML report is configured by default. For an optional, browser-readable HTML report, install the `pytest-html` plugin in the active virtual environment:

```bash
python -m pip install pytest-html
```

Then run the tests with HTML output enabled:

```bash
python -m pytest -m "ui or api" --user-id <your-user-id> --html=artifacts/report.html --self-contained-html
```

The report is saved to `automation/artifacts/report.html`. Open that file in a browser to review the results. Pytest can still generate the report when tests fail, as long as it completes the test run. The plugin is optional and is not included in the project's declared dependencies.

### E. Manual evidence versus automated evidence

| Location | Contents |
|---|---|
| `evidence/` | Screenshots associated with the manually documented defects |
| `automation/artifacts/screenshots/` | Screenshots generated by eligible failed UI test runs |
| `automation/artifacts/results.xml` | Optional JUnit XML test-results report |
| `automation/artifacts/report.html` | Optional HTML report generated with `pytest-html` |

The `artifacts/` directory is generated output. It is excluded from Git and may not exist until a test produces an artifact.

Review screenshots and reports before sharing them because they may contain application or test-user information.

## 11. Code Quality Checks

Run Ruff from `automation/` with the virtual environment activated.

### Check for lint issues

```bash
python -m ruff check .
```

### Check formatting without modifying files

```bash
python -m ruff format --check .
```

The formatting command checks files without changing them. If formatting needs to be applied intentionally, use:

```bash
python -m ruff format .
```

## 12. Project Structure

```text
repository-root/
├── test-plan.md
├── bug-report.md
├── strategy-and-recommendations.md
├── evidence/
└── automation/
    ├── pyproject.toml
    ├── conftest.py
    ├── .venv/                         # Local Python environment
    ├── artifacts/                     # Generated reports and screenshots
    │   ├── screenshots/
    │   └── results.xml
    ├── src/
    │   └── sporty_automation/
    │       ├── api/
    │       │   └── client.py
    │       ├── pages/
    │       │   ├── betting_page.py
    │       │   └── components/
    │       ├── ui/
    │       │   └── base.py
    │       ├── config.py
    │       ├── test_data.py
    │       └── util/
    └── tests/
        ├── api/
        │   └── test_insufficient_balance.py
        ├── ui/
        │   └── test_single_bet.py
```

### Key files

- `pyproject.toml` — project metadata, dependency declarations, pytest configuration, and Ruff settings.
- `conftest.py` — shared pytest fixtures, command-line options, browser lifecycle, and screenshot-on-failure hook.
- `src/sporty_automation/api/client.py` — API client used by tests.
- `src/sporty_automation/pages/` — page objects and reusable UI components.
- `src/sporty_automation/ui/base.py` — shared Selenium interactions and synchronization helpers.
- `tests/ui/` — UI automation.
- `tests/api/` — API automation.

## 13. Important Test Behavior and Known Limitations

### Expected failures

The application has known defects documented in `bug-report.md`, including past-match eligibility, insufficient-balance enforcement, balance consistency, filter behavior, and receipt details.

An automated test may therefore fail when it encounters one of these defects. Investigate the reported expected-versus-actual behavior before deciding whether the cause is an application defect, an automation issue, or a test precondition.

### Account balance and test data

- The UI test may place a bet and change the account balance.
- The API test depends on a suitable starting balance and does not automatically reset it.
- The framework does not guarantee a fresh, provisioned account.
- Avoid using the same account for repeated automated runs and manual testing.

### Minimum stake ambiguity

The specification conflicts on the minimum stake, stating €1.00 in one place and €1.01 in another. The test data uses €1.01 provisionally; the ambiguity should be clarified before relying on the disputed boundary.

## 14. Troubleshooting

### Python 3.11 is not found

Verify the installation:

```bash
python3.11 --version
```

On Windows, use:

```powershell
py -3.11 --version
```

Open a new terminal after installation and check your PATH if the command is unavailable.

### Virtual environment activation fails

Make sure you are inside the `automation/` directory and that `.venv/` was created successfully.

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use an approved environment-specific approach or activate the environment through Command Prompt instead.

### pytest or another package is missing

Make sure `.venv` is activated, then run:

```bash
python -m pip install -e ".[dev]"
```

Using `python -m pip` helps ensure that packages are installed into the Python environment currently running the command.

### Chrome or ChromeDriver fails to start

- Confirm Google Chrome is installed.
- Check network or proxy restrictions that may prevent Selenium Manager from obtaining a compatible driver.
- Read the complete terminal traceback.
- Retry with `--headed` if you need to inspect browser behavior.

### The application returns Unauthorized

Use a valid, provisioned test user:

```bash
python -m pytest -m "ui or api" --user-id <your-user-id>
```

Do not assume a generated user ID is automatically authorized.

### A test fails

1. Read the complete pytest failure output.
2. Identify the assertion or exception.
3. Compare the expected and actual values.
4. Check the INFO and error logs.
5. For eligible UI failures, open the screenshot referenced in the output.
6. Check the manual defect report for a matching known issue.
7. Determine whether the cause is the application, the automation code, the test account, or the environment.

## 15. Git and Generated Files

Do not commit the local virtual environment or generated Python caches and test artifacts.

The `.gitignore` should exclude at least:

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
artifacts/
```

Keep the manually curated `evidence/` directory tracked if the screenshots are referenced by `bug-report.md`.

