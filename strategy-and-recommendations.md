# Strategy and Recommendations

## 1. Automation Strategy

The two automated tests were selected based on business risk, user impact, and the value of repeatable validation.

### Test 1: TC-01 — Single Bet Placement (UI)

The single-bet journey is the core functionality of the application. This test validates the flow from filtering the dates, selecting a match and entering a stake to checking the potential payout, submitting the bet, and verifying the receipt and balance update.

Automating this journey helps detect inconsistencies between the bet slip, success receipt, and account balance. These checks are particularly important because manual testing identified incorrect receipt details and stale balance information.

### Test 2: TC-06 — Insufficient Balance Validation (API)

This test verifies that the API rejects a bet when the stake exceeds the user's available balance and that the balance remains unchanged after rejection.

This rule is critical to financial integrity. During testing, the API accepted an unaffordable bet and allowed the balance to become negative. API-level automation provides a direct check of this business rule without depending on the UI.

The test requires a starting balance within the supported minimum and maximum stake limits so that a valid stake can be submitted that exceeds the available balance. The API does not provide a way to set the balance per request, and the test does not currently establish this precondition automatically. Reliable execution therefore depends on suitable test-account state.

## 2. Manual Testing Coverage

Only TC-01 and TC-06 were selected for automation, as required by the assignment. The remaining planned scenarios were executed manually, including exploratory checks. Defects identified during these activities are documented in `bug-report.md`, with reproduction steps, expected and actual results, business impact, and supporting evidence where available.

Manual testing covered:

- **Past-match eligibility:** Whether past matches are displayed and can be selected for betting.
- **Date and odds filters:** Valid and invalid ranges, filter reset behavior, and whether displayed results match the selected criteria.
- **Stake validation:** Minimum and maximum stakes, decimal precision, and insufficient-funds scenarios.
- **Receipt and balance consistency:** Whether match details, selection, stake, odds, payout, and balance remain consistent across the bet slip, receipt, UI, and API.
- **Exploratory checks:** Unexpected behavior and discrepancies beyond the predefined scenarios.

These scenarios remain candidates for future automation, prioritised by business risk and the value of repeatable regression coverage.

## 3. Recommendations for Scaling

### 1. Integrate automated tests into CI/CD

Run the UI and API tests in a controlled pipeline, retain test reports and failure screenshots, and make failures visible to the team. Distinguish application defects from environment, setup, and test-data failures so results can be investigated efficiently.

### 2. Establish reliable test data and account isolation

Use provisioned, isolated test accounts with verified starting balances. Establish a predictable way to prepare and verify account state before each test, and verify balance changes through the API rather than relying only on the UI. Avoid shared accounts and uncontrolled repeated bet placement, which can affect subsequent tests.

### 3. Clarify requirements and expand risk-based coverage

Resolve the specification's conflicting minimum stake values (€1.00 versus €1.01) and clarify the timezone used for match eligibility and kickoff-time display. Once the known defects are addressed, prioritise automating past-match rejection, stake boundaries, filter validation, and receipt consistency. These areas are important because failures can affect betting eligibility, financial integrity, and user trust.

## 4. Current Limitations and Test Status

Both automated tests currently fail due to existing application defects.

- **TC-01 — UI single-bet placement:** The test executes but fails when application behavior differs from the expected requirements.
- **TC-06 — API insufficient-balance validation:** The test is intended to verify that an unaffordable bet is rejected without changing the balance. It depends on a suitable starting balance, which is not established automatically because the API does not support setting the balance per request. The application has also has a defect where it accepted an unaffordable bet and allowed the balance to become negative.

The tests retain their expected assertions rather than weakening them to produce passing results. The remaining scenarios were tested manually, and the identified defects are documented separately in `bug-report.md`.
