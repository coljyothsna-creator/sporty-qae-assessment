# Test Plan — Single Bet Placement

## 1. Objective

To validate the Single Bet Placement feature of the Sporty Group QA Engineer assignment, focusing on the critical betting journey, functional correctness, stake validation, and enforcement of business rules.

The testing aims to identify discrepancies between the feature specification and the application's actual behavior through prioritized manual testing, exploratory testing, and targeted automation.

## 2. Scope

### 2.1 In Scope

- Display of upcoming football matches, including home and away teams, kickoff date/time, and Home/Draw/Away odds.
- Bet selection and replacement of an existing selection.
- Bet slip functionality, including stake entry, available balance, potential payout, and removal of selections.
- Stake validation against the defined minimum, maximum, decimal precision, and available balance.
- Successful bet placement, balance deduction, and confirmation receipt.
- Bet-placement failure handling, error feedback, and retry behavior.
- Date and odds filtering, including invalid odds-range validation.
- Relevant API validation and business-rule enforcement.
- Exploratory testing to identify discrepancies between the specification and the implementation.

### 2.2 Out of Scope

- Live betting.
- Accumulators or multi-bets.
- Sports other than football.
- Mobile-specific user experience requirements.
- Performance and load testing.
- Comprehensive security testing.
- Extensive cross-browser compatibility testing beyond the specified desktop Chrome environment.

## 3. Test Approach

A risk-based approach will be used to prioritize scenarios according to business impact and the potential consequences of failure.

Testing will combine:

- **Requirement-based testing:** Validate behavior against the feature specification.
- **Positive and negative testing:** Verify valid workflows and appropriate handling of invalid inputs.
- **Boundary-value testing:** Check relevant stake limits and other defined boundaries.
- **Exploratory testing:** Investigate application behavior and identify potential defects beyond the explicitly planned scenarios.
- **Manual execution:** Execute the three highest-priority scenarios and document actual results and defects.
- **Targeted automation:** Implement the two automated tests required by the assignment: one UI end-to-end test and one API validation/business-rule test.

Observed behavior will be compared with the documented requirements. Any discrepancy or unresolved requirement ambiguity will be documented rather than treated as a confirmed defect without sufficient evidence.

## 4. Test Environment and Configuration

| Configuration | Details |
|---|---|
| Application | Sporty Group QA Engineer assignment — Single Bet Placement |
| Application type | Desktop web application |
| Application URL | https://qae-assignment-tau.vercel.app/ |
| Browser | Latest desktop Google Chrome |
| Operating system | Record the actual OS used for testing |
| API documentation | Application URL followed by `/api/docs` |
| API specification | Application URL followed by `/api/docs?format=json` |
| API user context | `x-user-id` request header |
| Currency | EUR |
| Initial balance | €125.50 |
| Automation language | Python 3 |
| UI automation | Selenium WebDriver with Pytest |
| API testing | Python `requests` library |

## 5. Assumptions and Open Questions

### 5.1 Assumptions

- The hosted application and its documented API are the intended test targets.
- A valid test user context and relevant match data can be obtained.
- The documented feature requirements are the basis for expected results, except where ambiguities are explicitly identified.
- The initial balance is €125.50 unless changed by previous test activity.
- Testing will be performed in desktop Chrome; mobile-specific testing is outside the defined scope.

### 5.2 Open Questions

- **Minimum stake:** The business rules and UI validation copy specify €1.00, while one validation table specifies €1.01. The authoritative minimum requires clarification.
- **Match eligibility:** The feature is restricted to upcoming, pre-match football events. Any observed ability to place bets on past matches must be investigated against this requirement.
- **Timezone:** The specification does not clearly establish which timezone determines match eligibility and kickoff-time presentation.
- **Test-data state:** A repeatable approach may be needed to establish the required balance and user state for testing.

## 6. Prioritized Test Scenarios

Documenting 6 prioritized scenarios. Each scenario inludes-

- Test case ID and title.
- Priority: Critical, High, Medium, or Low.
- Risk rationale.
- Test steps.
- Expected result.

### TC-01 — E2E Happy path of a successful single bet placement

**Priority:** Critical

**Risk rationale:** Bet placement is the core business functionality of the application. Failure in this journey could prevent users from placing valid bets or result in incorrect bet details, payout calculations, or balance updates. Validating the complete journey ensures that bets are processed correctly and that the confirmation receipt accurately reflects the transaction.

**Test steps:**
1. Open the web application after appending the user-id to the url.
2. Click on Date filter and select a wide range of upcoming dates, click Apply.
3. Verify that all displayed matches fall within the selected date range.
4. Enter a valid stake in the Bet Slip with no more than two decimal places.
5. Click on Place Bet button.
6. Click on Close button.

**Expected result:**
1. The application loads successfully using the supplied user context.
2. Date filter is applied successfully.
3. Bet Slip is displayed after selection of the odds with accurate information about the match i.e. home team vs away team, Match Winner value, Odds, text field for the stake to be entered.
4. The stake value entered accurately updated the potential payout value in the Bet Slip.
5. Bet receipt is displayed upon placing the bet. Bet ID, Match name (home team vs away team), Stake, Odds, potential payout and the timestamp details are correct.
6. The available balance after a successful bet is decreased by the stake amount.

### TC02 - Date and Odds filter validation

**Priority:** High

**Risk Rationale:** Incorrect filtering may display matches outside the selected date range or odds range, making it difficult for users to find relevant betting options and potentially leading to decisions based on inaccurate results.

**Test Steps:**
1. Open the web application using the required `user-id` query parameter.
2. Open the Date filter, select a date range containing available upcoming matches, and click Apply
3. Verify that all displayed matches fall within the selected date range.
4. Open the Odds filter, enter `1` as the minimum odds and `3` as the maximum odds, and click Apply
5. Verify that the displayed odds fall within the selected inclusive range.
6. Reset the Odds filter and verify that the filter is cleared and the results update accordingly.
7. Reset the Date filter and verify that the filter is cleared and the results update accordingly.

**Expected Result:**
1. The application loads successfully using the supplied user context.
2. The date filter is applied successfully.
3. All displayed matches fall within the selected date range, including the start and end dates.
4. The odds filter is applied successfully with the selected minimum and maximum values.
5. All displayed odds fall within the inclusive range of `1` to `3`.
6. Resetting the Odds filter clears its selected values and updates the results accordingly.
7. Resetting the Date filter clears its selected values and updates the results accordingly.


### TC-03 — Negative Validation: Betting on Past Matches

**Priority:** Critical

**Risk Rationale:** Allowing bets on past matches violates the application's core betting eligibility rules and may result in invalid bets being accepted and processed.

**Test Steps:**
1. Open the web application using the required `user-id` query parameter.
2. Open the Date filter, select a past date or date range, and click Apply.
3. Select the odds for a match whose kickoff time is in the past.
4. Enter a valid stake and click Place Bet.

**Expected Result:**
1. The application displays matches matching the selected date range.
2. The application prevents the user from placing a bet on a past match and displays appropriate feedback.


### TC-04 — Negative Validation of Odds Filter Range

**Priority:** High

**Risk Rationale:** Accepting an invalid odds range may produce misleading results and prevent users from filtering betting options correctly.

**Test Steps:**
1. Open the web application using the required `user-id` query parameter.
2. Open the Odds filter and enter a minimum odds value greater than the maximum odds value.
3. Click Apply.

**Expected Result:**
1. The application rejects the invalid odds range and displays clear validation feedback. The invalid range is not applied.

### TC-05 — Negative Validation of Stake Amount

**Priority:** High

**Risk Rationale:** Incorrect stake validation may allow invalid bets or incorrect financial transactions, affecting the integrity of bet placement and account balance.

**Test Steps:**
1. Open the web application using the required `user-id` query parameter.
2. Select the odds for an upcoming match.
3. Enter a stake below the minimum allowed amount (e.g., €0.50).
4. Enter a stake above the maximum allowed amount (e.g., €100.10).
5. Enter a stake with more than two decimal places (e.g., €1.234).
6. Enter a stake greater than the available balance.

**Expected Result:**
1. The application loads successfully using the supplied user context.
2. The Bet Slip is displayed with the selected match and odds.
3. A validation message indicates that the minimum stake is €1.00, and the Place Bet button is disabled.
4. A validation message indicates that the maximum stake is €100.00, and the Place Bet button is disabled.
5. The stake field does not allow more than two decimal places, or the application rejects the invalid stake and disables the Place Bet button.
6. A validation message indicates that the stake cannot exceed the available balance, and the Place Bet button is disabled.

### TC-06 — API Validation: Reject Bet with Insufficient Balance

**Priority:** Critical

**Risk Rationale:** Accepting a bet that exceeds the user's available balance may result in invalid financial transactions and a negative account balance.

**Pre-condition:**
1. Confirm that the user's available balance is between the minimum and the maximum stake as a pre-condition to validate this negative test.

**Test Steps:**
1. Submit a bet-placement request through the API with a valid upcoming match ID, valid selection, and a stake of available balance incremented by 1 (Eg. if balance is 30euros, the stake needs to be 31euros)
2. Verify the API response and retrieve the user's balance again using the balance API.

**Expected Result:**
1. The API rejects the bet with an appropriate insufficient-balance error, and the bet is not placed.
2. The available balance remains €30.00 after the rejected request.

