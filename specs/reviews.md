# Applicant Reviews

## Goal

Show reviews from real applicants on the home page. Until there are enough real reviews, placeholder reviews fill the empty places.

## Decisions

| Topic | Decision |
| --- | --- |
| Who | Only an applicant. The reviewer enters their application reference (for example `APP-00010`) and WhatsApp number. The two must match a `Loan Application`. |
| When | An application with any status can get a review. The thank-you page links to the form directly after the applicant applies. |
| Limit | One review for each application. A second review for the same reference is refused with a clear message. The endpoint is rate limited. |
| Content | A rating from 1 to 5 stars and a comment of at most 300 characters. |
| Shown name | First name and last initial of the borrower, for example `Mwila K.`. The name comes from the borrower, not from the form. |
| Moderation | A new review is not published. A Loan Manager sets `is_published` in Desk. Only published reviews show. |
| Home page | A "What our clients say" section shows 3 cards in a row (one column on phones). The newest published reviews fill the cards first. Placeholders fill the cards that are left. When there are 3 published reviews, no placeholders show. |
| Placeholders | A constant list in `frontend/src/data/reviews.js`. They are never in the database or in reports. |
| Form | The home section has a **Leave a review** button that opens a dialog. The thank-you link opens it with `?review=1&application=<ref>`, so the reference is already filled in. |
| Manager alert | A "Reviews awaiting approval" number card on the Epasi workspace. |

## Data model

### Review (new)

Named `REV-{#####}`. Created from the public form only.

- `loan_application` (Link, unique), `borrower` (Link, read only), `display_name` (Data, read only).
- `rating` (Rating), `comment` (Small Text).
- `is_published` (Check, default 0).

Permissions: Loan Manager reads, writes and deletes. Nobody creates from Desk.

## API

- `epasi.api.public.get_reviews()`: guest, GET. Gives the 3 newest published reviews: `display_name`, `rating`, `comment`.
- `epasi.api.public.submit_review(application, whatsapp_number, rating, comment)`: guest, POST, rate limited. Checks the match and the one-review limit, then inserts an unpublished review.

## Phases

### Phase 15: Review shows on the home page

- `Review` DocType with validation (match, one per application, rating 1 to 5, comment length).
- `submit_review` and `get_reviews`.
- Home section with 3 cards: real reviews first, then placeholders.
- Tests: wrong number refused, second review refused, unpublished review not shown, placeholders count.

### Phase 16: Form and manager alert

- Dialog on Home, link from the thank-you page with the reference filled in.
- Number card "Reviews awaiting approval" on the workspace.
- E2E: apply, leave a review from the thank-you link, publish it in Desk, see it replace a placeholder on Home (desktop and phone sizes).
