# Loan Officers, Referrers and Commission

## Goal

Epasi pays people who bring in borrowers. There are two kinds:

- **Loan officers** work for Epasi. They sign in to Desk, enter walk-in applications and share a referral link.
- **Referrers** are outside affiliates. The loan manager adds them and gives them a link. They sign in only to see their own referrals.

Both earn commission on loans from the borrowers they bring in, when those loans are repaid.

## Decisions

| Topic | Decision |
| --- | --- |
| Who | One `Sales Agent` DocType with a type: `Loan Officer` or `Referrer`. Only the Loan Manager adds them. |
| Rate | Set on each sales agent: `commission_rate` (%) and `minimum_principal` (ZMW). Example: 15% above K10,000. |
| Base | Commission = rate × interest paid on the loan. Nothing if the principal is not more than the minimum. |
| When earned | When the loan is Closed (fully repaid). A defaulted loan earns nothing. |
| Rate snapshot | The loan copies the agent, rate and minimum when it is submitted. Later changes to the agent do not affect it. |
| One agent | An application has at most one sales agent. |
| Borrower lock | A borrower is linked to the first agent who brings them in. Later applications from that borrower go to the same agent, even with another agent's link or no link. |
| Loan without application | A loan created directly in Desk takes the borrower's agent when it is submitted. |
| Manager override | The manager can change the agent on an application or borrower before the loan is submitted. |
| Referral link | `https://<site>/epasi/apply?ref=<CODE>`. The code is made from the agent's first name (for example `MWILA`, then `MWILA2`), is unique, and the manager can edit it. |
| Link memory | The site saves the code in the visitor's browser for 30 days. A newer link replaces it. |
| Inactive agent | An inactive agent's link is ignored. Earned commission is still paid. |
| Walk-ins | An application created in Desk by a loan officer is linked to that officer, unless the borrower is already linked. |
| Payout | Each commission is Unpaid or Paid. **Mark Paid** sets the paid date and records an `Expense` with category `Commission`, so it reduces net profit. |
| Loan reopened | If a repayment is cancelled and the loan is no longer Closed, an Unpaid commission is deleted. A Paid commission is kept. |
| Officer access | Role `Loan Officer`. Reads and creates applications and borrowers, reads loans and commissions, only their own. Cannot issue loans or record repayments. |
| Referrer access | Role `Referrer` (website user). A page at `/epasi/partner` shows their link and their referrals: first name and last initial, status and commission. No phone numbers or amounts borrowed. |

## Data model

### Sales Agent (new)

Named `AGT-{#####}`.

- `agent_type` (Select: Loan Officer, Referrer), `full_name`, `whatsapp_number`, `user` (Link User), `is_active` (Check, default 1).
- Commission section: `commission_rate` (Percent), `minimum_principal` (Currency).
- Referral section: `referral_code` (Data, unique), `referral_link` (read only, shown with a copy button).
- Totals section (read only): `commission_earned`, `commission_paid`, `commission_unpaid`.

Saving an agent with a `user` gives that user the `Loan Officer` or `Referrer` role.

### Commission (new)

Named `COM-{#####}`. Created by the system only.

- `sales_agent`, `loan`, `borrower`, `principal`, `interest_paid`, `commission_rate`, `amount`.
- `status` (Unpaid, Paid), `earned_date`, `paid_date`, `expense` (Link Expense).

### Changes to existing DocTypes

- `Borrower.sales_agent`: the first agent who brought them in.
- `Loan Application.sales_agent`.
- `Loan.sales_agent`, `Loan.commission_rate`, `Loan.minimum_principal`: copied on submit.
- `Expense.category`: add `Commission`.

## Flows

**Referral visit.** The SPA reads `?ref=` on any page and saves it with a 30-day expiry. `submit_application` gets `referral_code`. The server finds the active agent with that code. If the borrower has no agent, it links the borrower to that agent. The application takes the borrower's agent.

**Loan closes.** `Loan.update_paid_amounts` sets status Closed. If the loan has an agent and its principal is more than the minimum, create a Commission for rate × interest paid.

**Mark Paid.** A button on an Unpaid commission, for the Loan Manager. It creates an Expense (today, `Commission`, amount, description with agent and loan) and sets the commission to Paid. Each change to a commission updates the agent totals.

**Walk-in.** A borrower or application that a loan officer creates in Desk takes the officer's agent. The application status and the `sales_agent` fields are permission level 1, so an officer cannot change them.

**Partner page.** `/epasi/partner` sends a visitor who is not signed in to `/login`. After sign-in it calls `epasi.api.partner.get_partner_summary`. The footer has a **Partner login** link.

## Phases (tracer bullets)

### Phase 10: Referrer link to commission

The thinnest slice through every layer: a manager adds a referrer, a visitor applies with the link, the loan is repaid and a commission appears.

- `Sales Agent` with type, name, rate, minimum and an auto referral code and link.
- `?ref=` saved in the browser and sent with the application.
- `sales_agent` on Borrower, Loan Application and Loan. Borrower lock.
- `Commission` created when the loan closes. Removed if the loan reopens while Unpaid.
- Tests: code generation, attribution and borrower lock, commission above and below the minimum, defaulted loan, reopened loan.
- E2E: open the referral link, apply, issue and repay the loan in Desk, see the commission.

### Phase 11: Pay commissions

- **Mark Paid** button and `Commission` expense category.
- Agent totals: earned, paid, unpaid.
- Tests: paying creates the expense and net profit drops by the amount.

### Phase 12: Loan officers

- `Loan Officer` role. Saving an agent with a user gives that user the role.
- Own-records-only access through `permission_query_conditions` and `has_permission` hooks.
- Walk-in applications linked to the officer who creates them.
- Officers see their referral link with a copy button.
- Tests: an officer sees only their own records and cannot submit a loan.
- E2E: sign in as an officer, enter a walk-in application, check the list shows only own records.

### Phase 13: Referrer page

- `Referrer` role (website user). `/epasi/partner` page in the SPA, behind login.
- API returns the referrer's link, totals and referrals with first name and last initial, status and commission.
- Tests: the API returns only the caller's referrals and no phone numbers.
- E2E: sign in as a referrer on a phone-size screen and see the page.

### Phase 14: Reports and test data

- `Commission Summary` report: per agent and period, earned (by `earned_date`), paid (by `paid_date`) and unpaid of the earned amount.
- Workspace cards under "Money at a glance": Unpaid Commissions and Commission Paid This Month. The six money cards show as two rows of three.
- Add a loan officer, a referrer and their records to the test data snapshot. The snapshot also keeps their users. **Generate Test Data** sets their password to `Epasi@2026test`:
  - `natasha@epasi.test`: loan officer Natasha Mulenga (Desk).
  - `bupe@epasi.test`: referrer Bupe Zulu (`/epasi/partner`).
