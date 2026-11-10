# Epasi Loans MVP Plan

## Goal

Epasi Money Solutions lends money against collateral in Mazabuka, Zambia. The MVP does two things:

1. A public website where a visitor applies for a loan, describes their collateral, uploads photos and gives a WhatsApp number.
2. A back office where loan managers follow up applications, issue loans, record repayments and see who owes money and how much profit the business makes.

The branding follows `references/epasi_banner.png`: gold on near-black, serif headings, the bull logo, and the tagline "Umo nchito ufukuma ku chunga."

## Decisions

| Topic | Decision |
| --- | --- |
| Applicant access | No login. A visitor submits a public form. Managers follow up on WhatsApp. |
| Loan plans | A `Loan Plan` DocType. Seed "2 Weeks" (27%, 14 days) and "1 Month" (40%, 30 days). Managers can edit rates and limits. |
| Amount limits | Each plan has a minimum and maximum amount in ZMW. |
| Interest | Flat, charged once. Total due = principal × (1 + rate). No rollover, no late penalty. |
| Rate snapshot | A loan copies the rate and term from its plan when it is created. Later plan changes do not affect it. |
| Repayment | Many partial payments per loan. A payment covers interest first, then principal. The loan closes when the balance is zero. |
| Overdue | A daily job marks unpaid loans past their due date as Overdue. |
| Collateral default | Collateral has a status. If the business sells it, the manager records the sale amount as recovery income. |
| Profit | Interest collected + collateral recovery − expenses. |
| Back office | Frappe Desk: forms, list views, a workspace with number cards, and script reports. |
| Roles | One role, `Loan Manager`, with full access to all Epasi DocTypes. |
| Public site | Vue 3 SPA with Frappe UI (espresso), styled to the banner. |
| Currency | ZMW. Set as the system default currency on install. |

## Application form fields

The public form collects:

- Full name
- WhatsApp number (required)
- NRC number
- Address or town
- Loan plan
- Amount (validated against the plan limits)
- Loan purpose: Personal, Business, Asset Financing, Education
- Collateral description
- Estimated collateral value
- Collateral photos (1 to 5 images, max 5 MB each)

The form shows the total to repay and the due date before the visitor submits.

## Data model

All DocTypes go in the existing `Epasi` module.

### Loan Plan

`plan_name` (unique, name), `interest_rate` (Percent), `term_days` (Int), `minimum_amount`, `maximum_amount` (Currency), `is_active` (Check).

### Borrower

One record per person. Named by the normalized WhatsApp number (for example `260972616440`), so a repeat applicant links to the same borrower.

`full_name`, `whatsapp_number`, `nrc_number`, `address`. Read-only section: `total_borrowed`, `total_outstanding`. They are sums over submitted loans, updated when a loan is submitted or cancelled and after each repayment.

A form button opens `https://wa.me/<number>`.

### Loan Application

`borrower` (Link), `loan_plan` (Link), `amount`, `purpose`, `status` (Pending, Contacted, Approved, Rejected), `rejection_reason`, `notes`. Collateral section: `collateral_description`, `estimated_value`. Photos are private File attachments on the application, named `<application>-collateral-<n>.<ext>` by the server. The form shows them in a gallery (`photos_html`). The public form resizes each photo to at most 1600 px before upload.

Form buttons: "Chat on WhatsApp", "Create Loan" (when Approved).

### Collateral

Created from the application when the loan is submitted, with status Held. `borrower`, `loan`, `description`, `estimated_value`, `assessed_value`, `status` (With Borrower, Held, Returned, Forfeited, Sold), `sale_date`, `sale_amount`. Photos copy across from the application.

Status changes allowed:

| From | To |
| --- | --- |
| With Borrower | Held, Returned, Forfeited |
| Held | With Borrower, Returned, Forfeited |
| Forfeited | Sold, Returned |
| Returned, Sold | none |

Forfeited needs a Defaulted loan. Returned needs a Closed loan. Sold needs `sale_date` and `sale_amount`; the sale section shows only when the status is Sold. `get_recovery_income(from_date, to_date)` sums `sale_amount` of sold collateral by `sale_date`.

### Loan (submittable)

`borrower`, `loan_application`, `loan_plan`, `principal`, `interest_rate`, `term_days`, `disbursement_date`, `due_date`, `interest_amount`, `total_due`. Read-only tracking: `interest_paid`, `principal_paid`, `outstanding`, `status` (Active, Overdue, Closed, Defaulted).

The controller copies `interest_rate` and `term_days` from the plan when `loan_plan` is set or changed, and computes `due_date`, `interest_amount`, `total_due`, `outstanding` and `status` on validate.

Status rules: Closed when a submitted loan has zero outstanding. Defaulted stays until the loan closes. Otherwise Overdue when the due date has passed, else Active.

Form buttons on a submitted loan: "Record Repayment" (not Closed) and "Mark Defaulted" (Active or Overdue). "Mark Defaulted" also sets the loan's With Borrower or Held collateral to Forfeited.

### Loan Repayment (submittable)

`loan`, `payment_date`, `amount`, `mode` (Cash, Mobile Money, Bank), `reference`. Read-only: `borrower`, `outstanding` (before payment), `interest_portion`, `principal_portion`.

On submit, the controller locks the loan, splits the amount (interest first) and updates the loan. The loan recomputes `interest_paid` and `principal_paid` from all its submitted repayments, so a cancel reverses the update. A payment larger than the outstanding balance, or against a draft or closed loan, is rejected.

### Expense

`expense_date`, `category` (Transport, Airtime, Rent, Salaries, Other), `amount`, `description`.

## Public API

`epasi.api.public` holds guest methods, rate limited by `frappe.rate_limiter`:

- `get_loan_plans()`: returns active plans with rate, term and limits.
- `submit_application(**form, photos)`: validates input, finds or creates the Borrower, creates the Loan Application, and saves the photos as private files attached to it. Returns the application name.

Photos go as base64 in the request. The method checks the count, size and image type before it saves them.

## Back office

### Workspace "Epasi"

The workspace is the home page for a Loan Manager after login. It answers three questions at a glance: what needs action today, who owes money, and how the business is doing.

All blocks use standard Frappe workspace parts: Number Card, Dashboard Chart, Quick List, Custom HTML Block and Shortcut. Number cards and charts get their values from whitelisted methods in `epasi.api.dashboard`, so one place holds the dashboard queries.

The layout, from top to bottom:

1. **Needs action today** (number cards, red or amber when above zero):
   - Pending applications
   - Loans due today
   - Overdue loans
   - Overdue amount
2. **Money at a glance** (number cards, with change against last month):
   - Total outstanding
   - Cash lent this month
   - Collected this month
   - Net profit this month
3. **Trends** (dashboard charts):
   - Lent vs collected, by week, last 12 weeks (bar)
   - Net profit by month, last 6 months (line)
   - Outstanding by status: Active vs Overdue (donut)
   - Loans by plan: 2 Weeks vs 1 Month (donut)
4. **Today's summary** (Custom HTML Block): one card that lists today's applications, disbursements, repayments and expenses with totals. It reads from `epasi.api.dashboard.get_today_summary`.
5. **Lists** (Quick Lists):
   - Newest pending applications
   - Loans due in the next 7 days
   - Overdue loans, oldest first
   - Latest repayments
6. **Shortcuts**: New Application, New Repayment, New Expense, Loan Application, Loan, Borrower, Collateral, Expense, and the three reports.

The workspace is visible only to the `Loan Manager` and `System Manager` roles. It must stay readable on a phone, so the number cards go two per row on a small screen (`epasi/public/css/epasi.css`).

Implementation notes:

- The number cards are `Custom` cards. Frappe shows percentage change only on `Document Type` cards. Their colors are fixed: amber or red for "Needs action today". The comparison with last month shows in the "Today's summary" block. It compares this month to date with the same days of last month.
- All four charts use one Dashboard Chart Source, `Epasi Chart`. Its method is `epasi.api.dashboard.get_chart`, which selects the data by chart name.
- "Outstanding by status" also shows Defaulted loans, because their balance is still owed.
- Quick Lists always show the newest records first. Frappe has no sort setting for them. "Overdue loans, oldest first" is in the Outstanding Loans report.
- The `add_to_apps_screen` hook shows Epasi on the desk apps screen, with the bull icon. A Loan Manager has only this app, so after login Frappe opens `/app/epasi`. `epasi/desktop_icon/epasi.json` gives the same icon on sites that use the icon grid.
- "Today's summary" is the Custom HTML Block `Epasi Today`, shipped as a fixture.
- `epasi.epasi.money` holds one `Ledger` for each money column (lent, collected, interest, recovery, expenses) and a `MoneySummary` for profit. The reports and the dashboard use them.

### Reports

- **Outstanding Loans**: one row per open loan with borrower, WhatsApp, due date, days overdue, outstanding. Answers "who owes us".
- **Profit Summary**: for a date range, shows interest collected, recovery income, expenses and net profit, with a daily breakdown.
- **Daily Operations**: for one date, lists applications received, loans disbursed, repayments and expenses.

## Public site

- `frontend/` holds a Vite + Vue 3 + Frappe UI app, built into `epasi/public/frontend`.
- Served at `/epasi`. The website home page redirects to it.
- Routes:
  - `/epasi`: landing page with the two rate cards, services, contacts and a "Apply now" button.
  - `/epasi/apply`: the application form.
  - `/epasi/thank-you`: confirmation with the reference number and a WhatsApp link to the managers.
- Gold and black theme tokens on top of espresso. Mobile first, because most visitors use phones.

Implementation notes:

- The SPA uses the espresso dark theme (`data-theme="dark"`) with `gold` and `night` Tailwind colors and Playfair Display for headings.
- `frontend/src/data/business.js` holds the contacts, services and tagline from the banner.
- Each rate card links to `/epasi/apply?plan=<plan>`, which selects that plan on the form.
- `/` redirects to `/epasi` with `website_redirects` (302).
- The logo and icon are cropped from the banner into `epasi/public/images`.

## Phases (tracer bullets)

Each phase cuts through every layer (DocType, controller, API, UI, tests) and ends with something a person can use.

### Phase 1: Apply and see it in Desk

- `Loan Plan` with the two seeded plans (install hook).
- `Borrower` and `Loan Application` with the minimum fields: name, WhatsApp, plan, amount.
- `Loan Manager` role.
- `get_loan_plans` and `submit_application` without photos.
- Vue app scaffold with a plain apply form.
- Tests: API creates a borrower and application, rejects an amount outside the plan limits, reuses the borrower for a repeat WhatsApp number.
- E2E: submit the form as guest, see the application in Desk.

### Phase 2: Collateral and photos

- Add the rest of the form fields and collateral fields.
- Photo upload in the form and in `submit_application`.
- "Chat on WhatsApp" button on Borrower and Loan Application.
- Tests: photo count, size and type checks. Files are private and attached.

### Phase 3: Issue a loan

- `Loan` DocType and controller calculations.
- "Create Loan" button on an approved application. It creates a draft loan and opens it. Only one loan (draft or submitted) per application.
- When the loan is submitted, the controller creates the `Collateral` record with status Held and copies the application photos to it.
- Tests: totals and due date for both plans. Rate snapshot does not change when the plan changes.

### Phase 4: Repayments

- `Loan Repayment` with interest-first allocation, submit and cancel.
- Loan closes at zero balance.
- Tests: partial payments, overpayment rejected, cancel reverses, close on full payment.

### Phase 5: Overdue and collateral recovery

- Daily scheduled job (`mark_overdue_loans`) marks Active loans past their due date as Overdue.
- Collateral status flow and sale fields.
- "Mark Defaulted" action on a loan.
- Tests: overdue job, sale amount counted as recovery.

### Phase 6: Money view

- `Expense` DocType.
- Outstanding Loans, Profit Summary and Daily Operations reports.
- Tests: report totals against known data.

### Phase 7: Manager dashboard

- `epasi.api.dashboard` methods for the number cards, charts and today's summary.
- Number Cards, Dashboard Charts, Quick Lists, Custom HTML Block and Shortcuts, exported as fixtures with the app.
- The Epasi workspace with the layout from "Back office".
- Tests: each dashboard method against known loans, repayments and expenses.
- E2E: log in as a Loan Manager and check that the workspace shows the expected values on desktop and phone sizes.

### Phase 8: Branded public site

- Landing page and thank-you page.
- Banner theme, logo, rate cards read from `get_loan_plans`.
- Repayment preview on the form.
- E2E on a phone-size viewport.
- Header and footer links for loan managers to sign in to the Epasi workspace.

### Phase 9: Test data

- `Epasi Settings` (single, System Manager only) with **Generate Test Data** and **Clear Test Data** buttons.
- The test data is a snapshot of borrowers, applications, loans, repayments, collateral, expenses and their photos, kept in `epasi/setup/test_data/` (`records.json` and `files/`).
- Generate inserts the records with their original names, values and status. It refuses if any of them already exist, and moves the naming counter past the highest test number so new records do not reuse a test name.
- Clear deletes only the records named in the snapshot, with their photos. Other records are kept.
- To refresh the snapshot from a site: `bench --site <site> execute epasi.setup.test_data.export`.
- Tests: generate, refuse a second generate, clear keeps other records, new names follow the test names.

## Out of scope for the MVP

- Borrower login and online status lookup.
- Automated WhatsApp or SMS messages.
- Mobile money integration.
- Rollover interest and late penalties.
- Capital and cash-on-hand bookkeeping.
- A custom manager dashboard outside Desk.
