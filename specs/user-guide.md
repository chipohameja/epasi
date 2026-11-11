# User Guide

## Goal

Each type of user has one guide page with steps, screenshots and examples in simple English.

## Decisions

| Topic | Decision |
| --- | --- |
| Place | Public pages in the website: `/epasi/guide` lists the guides, `/epasi/guide/<slug>` shows one. |
| Guides | Applicant, Referrer, Loan Officer, Loan Manager, Administrator. |
| Content | One data file for each guide in `frontend/src/data/guides/`. Each section has text, steps, a screenshot, an example and a tip, all optional. |
| Screenshots | `epasi/public/images/guide/`, served from `/assets/epasi/images/guide/`. Website pages at phone size, Desk pages at 1280 × 800. |
| Links | "User guide" in the website footer. "User Guide" shortcut in the Epasi workspace. |
| Secrets | No passwords in the guides. The pages are public. |

## Refresh the screenshots

Load the test data (Epasi Settings), then take the screenshots again with agent-browser. Fill forms with the examples from the guide, but do not save them.
