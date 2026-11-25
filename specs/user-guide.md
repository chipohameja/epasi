# User Guide

## Goal

Each type of user has one guide page with steps, screenshots and examples in simple English.

## Decisions

| Topic | Decision |
| --- | --- |
| Place | Desk page `user-guide` (a Frappe UI page). `/desk/user-guide` lists the guides, `/desk/user-guide/<slug>` shows one. Only System Manager can open it. |
| Guides | Applicant, Referrer, Loan Officer, Loan Manager, Administrator. |
| Content | One data file for each guide in `epasi/epasi/page/user_guide/guides/`. Each section has text, steps, a screenshot, an example and a tip, all optional. |
| Screenshots | `epasi/public/images/guide/`, served from `/assets/epasi/images/guide/`. Website pages at phone size, Desk pages at 1280 × 800. |
| Links | "User Guide" shortcut in the Epasi workspace. Desk shows it only to users who can open the page. The website has no link. |
| Secrets | No passwords in the guides. The page is for admins, but its script and screenshots are public static files. |

## Refresh the screenshots

Load the test data (Epasi Settings), then take the screenshots again with agent-browser. Fill forms with the examples from the guide, but do not save them.
