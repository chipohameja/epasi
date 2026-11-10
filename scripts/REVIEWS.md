# QA Review — `61a10ab` fix(payment-import): skip MovimentiCC card lines not booked yet

**Status: ✅ APPROVED**

Both findings from the `388bd56` review are fixed as suggested. No new issues come from this commit.
The desk e2e for MovimentiCC is still blocked by the missing card *5688 Bank Account (`00 §8`).

## What was verified

| Check | Result |
|---|---|
| `test_parsers` (33 tests) on `beb-test.localhost` | ✅ all pass |
| `test_payment_import` (19 tests) on `beb-test.localhost` | ✅ all pass (33.1 s) |
| Old finding 1: `-da contab` lines | ✅ the 7 fixture lines on 17/08 are `Skipped` with "Not booked by the bank yet." (the same text as Lista `prenotata`). The booked `iliad` line and the €1600 transfer are still Created (9 rows / 2 Created / 7 Skipped) |
| Skip order in the importer | ✅ `skip_reason` is checked before the currency check and `fingerprint()`, so a skipped line takes no occurrence number. When the bank later books the line, its occurrence count does not depend on the pending lines |
| Marker edge cases (bench console) | ✅ upper case `-DA CONTAB` and trailing spaces → Skipped. `-da contab` in the middle of the text, `- da contab` and `-da contabilizzare` → not skipped. This is the right choice: only the exact suffix the bank writes is matched |
| Old finding 2: `bon.da … fattura` ignores case | ✅ `BON.DA ACME SRL FATTURA 12` → `ACME SRL`, `Bon.Da Foo Bar Fattura 1` → `Foo Bar`. New test covers it |
| Tests are real regression tests | ✅ the import test now asserts 2 Created / 7 Skipped, so it fails if the skip is removed. The parser test also checks that the booked last line is not skipped |
| Existing data | ✅ `site1.local` has no `Movimenti CC` import (only Multipla, Lista and one empty-format failed run), so no pending card line was ever saved as a Bank Transaction and nothing needs cleaning up |
| Specs | ✅ `02 §5` has the rule, `09` has Q24 (marked "Not confirmed with the bank yet"), PROGRESS is updated (123 tests). They are git-ignored, so they are not in the commit |

The desk was not checked with agent-browser: no Bank Account can take MovimentiCC files on
`site1.local` yet, and no form or UI code changed.

## Findings

None.

## Notes (no action)
- `MovimentiCcParser.skip_reason` returns `None` for a booked line, while `StatementLine.skip_reason`
  defaults to `""`. The importer only tests truthiness, so this is harmless.
- Q24 is still an assumption. When the first real MovimentiCC export after a booking is available,
  check that the booked line really has no `-da contab` suffix and that the €1 PayPal
  verification pairs either show up booked or disappear.
- A skipped row's dates and amount are still parsed, so a pending line with a bad date fails as
  "Row N: invalid date". Lista instead skips the `VALUTA` parse for pending rows. Both are fine,
  since MovimentiCC pending lines carry real dates.
- The `.gitignore` change and `references/payments/` are still uncommitted and were not reviewed.

---

# QA Review — `388bd56` feat(payment-import): read MovimentiCC statements

**Status: ✅ DONE — findings 1–2 fixed (`-da contab` lines Skipped, Q24; pattern case-insensitive)**

~~**Status: ⚠️ APPROVED WITH A QUESTION**~~

TB-I2 slice 3 parses the MovimentiCC layout correctly. Detection, signed amounts, the
`bon.da … fattura` payer and the currency check all work, from both CSV and XLSX. One question
must be answered before real MovimentiCC files are imported (finding 1): 7 of the 9 fixture lines
look like card movements the bank has not booked yet. The desk e2e is still blocked by the missing
card *5688 Bank Account, as `00 §8` and PROGRESS say.

## What was verified

| Check | Result |
|---|---|
| `test_parsers` (31 tests) on `beb-test.localhost` | ✅ all pass |
| `test_payment_import` (19 tests) on `beb-test.localhost` | ✅ all pass (28.8 s) |
| Fixture = `references/payments/MovimentiCC_OnLine_21_08…csv` | ✅ byte-identical |
| Spec conformance (`02 §2` header, `§5` signed `Importo` + `Causale` in `raw`, `§6` payer pattern, `00` file map) | ✅ |
| Detector | ✅ no header clash with Multipla (`DATA`/`VALUTA` vs `Data contabile`). The unknown-format message now lists all three formats |
| XLSX (bench console, `as_xlsx` of the fixture) | ✅ 9 lines, sum €1233.96, `Divisa` = `"EUR"` as text, same as the CSV |
| Delimiter guess | ✅ a description with 8 commas is still read with `;` (6 `;` + amount comma per row) |
| `short_payer_name` on other formats | ✅ no `bon.da` in any BCC/PayPal reference file, so Multipla/Lista payer names are unchanged |
| Identical €1 card lines on the same day | ✅ the occurrence number keeps them apart (9 Created in the new test) |
| Test quality | ✅ the currency is swapped to `INR` on the test company, as for the other formats, so the import test reaches `Created` |

The desk was not checked with agent-browser: no Bank Account can take these files on
`site1.local` yet (documented in `00 §8`), and no form or UI code changed.

## Findings

### 1. ✅ Fixed — [Medium / question] Card lines marked `-da contab` are imported as booked movements
`parsers/movimenti_cc.py`, `importer.py:101-107`

Seven fixture lines (all on 17/08, four days before the 21/08 export) end with `-da contab`.
This most likely means *da contabilizzare*, i.e. card authorisations the bank has not booked yet:
- they have `Data contabile` = `Data valuta`, while the booked `iliad` line has 10/08 vs 04/08
  (the usual card settlement delay) and no `-da contab`;
- they are PayPal €1 verification charges and their `storno` (reversals), plus one €359.05 charge.

If so, they are the same case as Lista's `prenotata` rows, which the spec skips (`02 §5`).
Today each becomes a Created Bank Transaction. The fingerprint holds `posting_date` and
`value_date`, so when the bank later books the €359.05 with its real dates, the next export
creates a **second** Bank Transaction for the same payment. The €1 pairs may also never appear
as booked lines at all.

**Ask:** confirm the meaning of `-da contab` with the user or the bank. If they are pending, give
them `skip_reason = "Not booked by the bank yet."` (as Lista does), add a test, and add the rule to
`02 §5`. If they are booked, note that in `02 §5` so the question is not raised again.

### 2. ✅ Fixed — [Low] The `bon.da … fattura` pattern is case-sensitive
`signals.py:7`

`BONIF. VS. FAVORE - BON.DA ACME SRL FATTURA 12` gives no payer name (checked in the console),
while `end_to_end_id` already uses `re.IGNORECASE`. The fixture is lowercase, so nothing fails
today. Adding `re.IGNORECASE` is a one-word change and makes the fallback safe if the bank's
wording changes case.

## Notes (no action)
- The payer name is kept lowercase (`spacesonic epe`) in `bank_party_name`. Matching is not
  affected, because `name_tokens` lowercases both sides.
- Card lines have no payer, End-to-End ID or RIF, so `reference` is the first 140 characters of
  the description. This is the same as finding 6 of the `2001c54` review (deferred to TB-I3).
- No XLSX test for MovimentiCC. It was checked in the console (see above), and the reader path is
  shared with Lista, which has one.
- The `.gitignore` change and `references/payments/` are still uncommitted and were not reviewed.

---

# QA Review — `a67445c` fix(payment-import): read unexpected XLSX cells as row errors

**Status: ✅ APPROVED**

Finding 1 from the `295708f` review is fixed as suggested. Every cell type from that review now
gives either a correct line or a "Row N: invalid …" message. No new issues come from this commit.

## What was verified

| Check | Result |
|---|---|
| `test_parsers` (28 tests) on `beb-test.localhost` | ✅ all pass |
| `test_payment_import` (18 tests) on `beb-test.localhost` | ✅ all pass (30.1 s) |
| Old finding cases (bench console, built XLSX → reader → detector → parser) | ✅ serial date `46240` → "Row 2: invalid date '46240'". Numeric Multipla/Lista description `12345` → `"12345"`. Amount `TRUE` → "Row 2: invalid amount 'True'". Lista `DIVISA` `978` → now the corruption message (no `TypeError`) |
| Extra cell types | ✅ a time-only cell or `TRUE` in a date column → "invalid date". A Lista `VALUTA` serial number → "invalid date". A float description `12345.5` → `"12345.5"`. Multipla `DIVISA` `978` → `"978"`, which the importer then marks `Rejected` (other currency) |
| `VALUTA` in Lista `text_columns` | ✅ no regression for real Excel dates: the reader already turns `datetime` into `dd/mm/yyyy` before `str()`, and `prenotata` is still `Skipped` |
| Real Excel file on `site1.local` (`PAY-IMP-2026-0006`, parsed only) | ✅ 123 lines, all `EUR`, 1 pending row skipped. This is the same result as before the change |
| `record()` merge | ✅ every `text_columns` name is in the header signature, so `record[name]` always exists once the header matches |
| Spec `03 §2` note from the last review | ✅ now says `.csv` or `.xlsx` and "Only CSV and XLSX files are supported." |

The desk was not checked with agent-browser. This commit only changes parser code, and no form or
UI code changed.

## Findings

None.

## Notes (no action)
- Lista `DARE`/`AVERE` holding `FALSE` is read as `0` because of `record[...] or "0"`, while `TRUE`
  is an error. Excel never writes a boolean into an amount column, so this is harmless.
- `except AttributeError` is only around `value.strip()` in the two helpers, so it cannot hide a
  parser bug.
- The `.gitignore` change and `references/payments/` are still uncommitted and were not reviewed.

---

# QA Review — `295708f` feat(payment-import): read XLSX statements and reject other currencies

**Status: ✅ DONE — finding 1 fixed in `a67445c`**

~~**Status: ✅ APPROVED**~~

TB-I2 slice 2 meets its goal. A real Excel-saved Lista imports with the same result as the CSV,
an unreadable workbook fails with a clear message, and a line in another currency becomes a
`Rejected` row while the other lines still import. One low-severity finding comes from cells
whose type is not what the parser expects. It can go into slice 3.

## What was verified

| Check | Result |
|---|---|
| `test_parsers` (26 tests) on `beb-test.localhost` | ✅ all pass |
| `test_payment_import` (18 tests) on `beb-test.localhost` | ✅ all pass (28.1 s) |
| Real Excel save on `site1.local` (`PAY-IMP-2026-0006`, `ListaMovimenti13_09.xlsx`) | ✅ the file really holds `datetime` dates, `int`/`float` amounts, `None` for empty cells and `"prenotata"` as text. Completed, BCC Lista, 122 Duplicate / 1 Skipped / 0 created. This matches `0004` (69 + 53 = 122 non-pending rows) |
| Desk (agent-browser) on `0006` | ✅ Completed, BCC Lista, the `.xlsx` attachment and the new help text "CSV or XLSX statement exported from the bank" are shown |
| XLSX numbers (bench console) | ✅ float `1234.56` → `Decimal("1234.56")`. Italian text `"1.234,56"` in an XLSX is still read correctly. A date given as text (`"06/08/2026"`) works next to a real `datetime` |
| Unreadable / wrong files | ✅ a CSV renamed to `.xlsx` gives "This XLSX file cannot be read…" (`PaymentImportError`, not logged). `.pdf` gives "Only CSV and XLSX files are supported." on both `validate()` and the reader. A 0-byte upload cannot happen: Frappe refuses a `File` with empty content ("File does not exist") |
| `read_xlsx_file_from_attached_file` | ✅ returns lists, so `record()`'s `row + [""] * n` (note from the `0c991d8` review) still works. Only the active sheet is read, which is fine for one-sheet bank exports |
| Currency check order | ✅ it runs before `fingerprint()`, so a `Rejected` line does not take an occurrence number. This matches the patch, which already skips `Rejected` rows |
| `error_count` | ✅ counts `Rejected` + `Error` → "Completed with Errors", as in `00` and `03 §6` |
| `bank_account_currency` in the constructor (outside the `try` in `run_import`) | ✅ no new stuck-import risk: `get_value` returns `None` and does not raise. `site1.local` `BCC c/c - BCC` → `EUR` |
| Rewritten error-row test | ✅ still a real test of the `Error` path (forces one insert failure and checks the row message), now that a bad currency is `Rejected` |

## Findings

### 1. ✅ Fixed — [Low] Unexpected non-text XLSX cells fail the whole import with a raw Python message
`reader.py` `cell()`, `formats.py` `parse_italian_date` / `parse_italian_amount`, `bcc_multipla.py:22-23`, `bcc_lista.py`

The reader now keeps numbers as numbers in **every** column, but the parsers still expect text in
the text and date columns. Checked in the console with small workbooks:

| Cell | Result |
|---|---|
| date column holding an Excel serial number (`46240`, the date format was lost) | `AttributeError: 'int' object has no attribute 'strip'` |
| Multipla `DESCRIZIONE` that is only digits (`12345`) | `AttributeError: 'int' object has no attribute 'strip'` |
| Lista `DESCRIZIONE_OPERAZIONE` that is only digits | `TypeError: expected string or bytes-like object` (from `DescriptionSignals`) |
| Lista `DIVISA` as a number (`978`) | `TypeError` from `check_not_resaved` instead of the corruption message |
| amount cell `TRUE` | `decimal.InvalidOperation` (`bool` passes the `int` check) |

None of these are `StatementValueError`, so the whole file fails, the run is logged as a bug, and
the user sees the raw Python text with no row number. Such cells are rare in a bank export, so
this is low severity. **Fix:** in `parse_italian_date` / `parse_italian_amount`, raise
`StatementValueError` for any other type (and reject `bool`). Read text fields with `str(...)`
(e.g. in `StatementParser.record()` for every column a parser treats as text, or in the parsers).
Add a test with a numeric description and a serial-number date.

## Notes (no action)
- A lowercase currency (`eur`) is `Rejected` with "Currency eur differs from … EUR". Bank exports
  use upper case, so this is fine. `str.upper()` would make it safe if a future format differs.
- The XLSX tests build the workbook from the CSV fixture (`as_xlsx`), and `excel_value` also turns
  `CAUSALE ABI` codes into floats. This is close to what Excel does, and the real Excel file on
  `site1.local` agrees.
- Spec `03 §2` still says "file extension `.csv` (`.xlsx` from TB-I2) | Only CSV files are
  supported." It should now say `.csv`, `.xlsx` and "Only CSV and XLSX files are supported."
  `02 §2`, `03 §6` and PROGRESS are up to date.
- The `.gitignore` change and `references/payments/` are still uncommitted and were not reviewed.

---

# QA Review — `7471b12` fix(payment-import): clear the detected format when a run starts

**Status: ✅ APPROVED**

Finding 1 from the `0c991d8` review is fixed as suggested. No new issues come from this commit.

## What was verified

| Check | Result |
|---|---|
| `test_payment_import` (16 tests) on `beb-test.localhost` | ✅ all pass (27.4 s) |
| `test_parsers` (22 tests) on `beb-test.localhost` | ✅ all pass |
| New test is a real regression test | ✅ with `importer.py:45` removed, `test_restart_with_an_unknown_file_clears_the_old_format` fails with `('Failed', 'BCC Lista') != ('Failed', None)`. With the line back, it passes |
| Reset placement | ✅ `detected_format = None` is set in `run()` before `parse()`, so every failure before detection (reader refusal, unknown layout) reports no format. `parse()` sets the format before `parser.parse()`, so a failure inside the parser (re-saved Lista) still shows the detected format (`test_resaved_lista_fails_with_a_clear_message` still passes) |
| Success path | ✅ `complete()` saves the format set by `parse()`. `test_lista_adds_only_the_days_missing_from_multipla` still checks `BCC Lista` |
| Other uses of `detected_format` | ✅ only `importer.py:24,45,64` and `PaymentImport.fail()`. Nothing else reads the stale value |

## Findings

None.

## Notes (no action)
- The open notes from the `0c991d8` review still apply (Lista row cut off before `DIVISA`, `record()`
  expects lists, which matters for the slice 2 XLSX reader).
- The `.gitignore` change and `references/payments/` are still uncommitted and were not reviewed.

---

# QA Review — `0c991d8` fix(payment-import): read short rows, keep parser bugs visible, show the format of failed imports

**Status: ✅ DONE — finding 1 fixed in `7471b12`**

~~**Status: ✅ APPROVED**~~

All three findings from the `cea6b6f` review are fixed and work as asked. One new low-severity
issue comes from fix 3. It is a one-line change and can go into slice 2.

## What was verified

| Check | Result |
|---|---|
| `test_parsers` (22 tests) on `beb-test.localhost` | ✅ all pass |
| `test_payment_import` (15 tests) on `beb-test.localhost` | ✅ all pass (25.1 s) |
| Old finding 1: short rows (bench console, reader → detector → parser) | ✅ Lista `…;10,00;EUR;;` and Multipla `…;10,00;EUR;;` both give €10.00 with an empty description. A Multipla row with only two cells now gives "Row 2: invalid amount ''" and no longer a bare `KeyError` |
| Old finding 2: only `StatementValueError` is treated as a user mistake | ✅ `parse_italian_amount` / `parse_italian_date` raise it. A `ValueError` from `DescriptionSignals` gets through to `run_import` and is logged (`test_parser_bug_is_not_reported_as_a_user_mistake`). The parsers have no other `KeyError` path left, because the padding fills every header column |
| Old finding 3: failed import keeps its format | ✅ A re-saved Lista on `site1.local` (console, rolled back) gives `Failed` + `BCC Lista`. Covered by `test_resaved_lista_fails_with_a_clear_message` |
| `BankTransactionImporter(...)` created outside the `try` | ✅ no new risk. The constructor only stores the doc. If the doc is missing, `get_doc` fails either way, as it did before |

## Findings

### 1. ✅ Fixed — [Low] A restarted failed import can show the format of the file it replaced
`importer.py:16,24` + `importer.py:63`

The importer now passes `importer.payment_import.detected_format` to `fail()`. That doc is loaded
from the database, so it already holds the format from the previous failed run. If the new run
fails **before** detection (unknown layout, or the reader refuses the file), the old value is kept.
Checked on `site1.local` (console, rolled back):

1. Upload the re-saved Lista → `Failed`, `BCC Lista`, "This file looks corrupted…"
2. Replace the file with an unknown CSV (allowed on a Failed import) and run again →
   `Failed`, **`BCC Lista`**, "Unrecognised file format…"

Before this commit the rollback always cleared the field, so this could not happen. **Fix:** clear
the field when a run starts, e.g. `self.payment_import.detected_format = None` at the top of
`run()` (or `parse()`). Add a test that runs a Lista import that fails, then an unknown file.

## Notes (no action)
- A Lista row cut off before `DIVISA` (`12/09/2026;12/09/2026;;10,00`) now reaches
  `check_not_resaved` with an empty currency and fails with the "re-saved with commas" message.
  That message is not quite right for this case, but such a row is unlikely in a real bank export.
- `record()` does `row + [""] * n`, so it expects `row` to be a list. `StatementReader` returns
  lists. Keep this in mind if the slice 2 XLSX reader returns tuples (openpyxl `values_only` does).
- `PAY-IMP-2026-0005` on `site1.local` still shows an empty format. It failed before this change,
  and nothing fills it in later. This is expected.
- The `.gitignore` change and `references/payments/` are still uncommitted and were not reviewed.

---

# QA Review — `cea6b6f` feat(payment-import): detect the statement format and import BCC Lista files

**Status: ✅ DONE — findings 1–3 fixed**

~~**Status: ✅ APPROVED**~~

TB-I2 slice 1 meets its goal. Lista imports into the right account, adds no duplicates over
Multipla, and the re-saved file fails with the message from the spec. Both findings from the
`31f9dfe` review are fixed. The two new findings are low severity and can go into slice 2.

## What was verified

| Check | Result |
|---|---|
| `test_parsers` (20 tests) on `beb-test.localhost` | ✅ all pass |
| `test_payment_import` (15 tests) on `beb-test.localhost` | ✅ all pass (28.2 s) |
| Lista vs Multipla overlap, compared day by day (bench console) | ✅ Multipla covers 06/08–21/08 and Lista covers 07/08–11/09. Every Multipla movement from 07/08 on is in Lista. The only Lista lines inside Multipla's range that are new are 2 lines on 21/08 (Multipla was exported that morning). So the 69 created rows are real new movements, not false new ones |
| `site1.local` imports | ✅ `PAY-IMP-2026-0004` Lista: Completed, 123 / 69 created / 53 Duplicate / 1 Skipped (row 124, €145, "Not booked by the bank yet."). `PAY-IMP-2026-0005` re-saved Lista: Failed with the corruption message |
| Patch on `site1.local` | ✅ in the Patch Log. All 296 Created/Duplicate rows recomputed with the new formula agree with the stored Bank Transaction fingerprints. No duplicate fingerprints |
| Desk (agent-browser) | ✅ `0005` shows Failed, the full message and "Start Import". A Failed import still lets the user replace the file. `0004` shows BCC Lista and the Skipped last row |
| Old finding 1 (bad line) | ✅ "Row 2: invalid amount '15,0x'" and "invalid date '…'" are raised as `PaymentImportError` |
| Old finding 2 (`PaymentImportError` location) | ✅ moved to `formats.py`. The reader, detector and parsers import it from there |
| Patch occurrence counting vs runtime | ✅ both skip only `Skipped` (and the future `Rejected`) rows and count Duplicate and Error rows, so the occurrence numbers match |
| Specs / PROGRESS | ✅ `02 §5`, `03 §4`, `09` Q23 and PROGRESS are updated (they are git-ignored, so they are not in the commit) |

## Findings

### 1. ✅ Fixed — [Low] A row whose last cells are empty fails the whole import with an unclear message
`reader.py` `clean()` + `formats.py:59`

`StatementReader.clean()` removes empty trailing cells, and `records()` zips with `strict=False`,
so the trailing columns are simply missing from the record. A Lista row with an empty description
and no ABI code (`12/09/2026;12/09/2026;;10,00;EUR;;`) gives a `KeyError`. Checked in the console:
the import fails with **`Row 2: 'DESCRIZIONE_OPERAZIONE'`**. Multipla has the same problem with
`DESCRIZIONE`, its last column. Such rows are rare, but one of them stops the whole file, and the
message does not tell the user what is wrong.

**Fix:** fill in the missing columns in `records()` (e.g. `{name: row[i] if i < len(row) else ""
for i, name in enumerate(header)}`). This fixes every parser in one place. Add a test with an
empty description.

### 2. ✅ Fixed — [Low] `parse_record` treats every `ValueError`/`KeyError` as a user mistake
`formats.py:64-68`

Bad amounts and dates now raise a clear `ValueError`, which is good. But the `except` also catches
any `ValueError` or `KeyError` from a bug in a parser or in `DescriptionSignals`. Those become
`PaymentImportError`, so `run_import` does not log them. That is the same blind spot that
`31f9dfe` closed for `complete()`. It matters more as slices 2 and 3 add the XLSX reader and
`MovimentiCcParser`. **Fix:** raise a small `StatementValueError(ValueError)` from
`parse_italian_amount` / `parse_italian_date` (and for missing columns, after finding 1) and catch
only that.

### 3. ✅ Fixed — [Info] A failed import does not show the detected format
`PAY-IMP-2026-0005` was detected as BCC Lista, but `detected_format` is empty because the rollback
undoes it before `fail()`. This would help when someone looks into a failed upload. Optional:
set it in `fail()`, or set it with `db_set` after the rollback.

## Notes (no action)
- Dropping the description from the fingerprint is a deliberate trade-off (`03 §4`, Q23). The
  reference files show no false duplicates. A pending Lista row and its later booked line are
  handled correctly, because pending rows are skipped before the fingerprint is computed.
- `test_patch_recomputes_old_fingerprints` covers only an import where every row is Created. An
  import that mixes Duplicate and Created rows on the same day is not tested, but it was checked on
  `site1.local` (see above).
- The new Lista fixtures hold real counterpart names and IBANs, as the Multipla fixture already
  does. Keep this in mind if the repository is ever made public.
- The `.gitignore` change and `references/payments/` are still uncommitted and were not reviewed.

---

# QA Review — `31f9dfe` fix(payment-import): log unexpected failures, skip only the importer's own errors

**Status: ✅ DONE — findings 1–2 fixed in TB-I2 slice 1**

~~**Status: ✅ APPROVED**~~

Finding 1 from the `fa2f57c` review is fixed as suggested. No new issues come from this commit.
Two notes below are about older code and can go into TB-I2.

## What was verified

| Check | Result |
|---|---|
| `test_payment_import` (12 tests) on `beb-test.localhost` | ✅ all pass (18.7 s) |
| `test_parsers` (11 tests) on `beb-test.localhost` | ✅ all pass |
| `TimestampMismatchError` is a `ValidationError` but not a `PaymentImportError` (bench console) | ✅ so it is now logged |
| Test now uses `frappe.TimestampMismatchError` and asserts `log_error` is called once | ✅ the old `isinstance(error, frappe.ValidationError)` check would fail this test, so it is a real regression test |
| `test_unknown_file_fails_without_an_error_log` | ✅ still passes; "Unrecognised file format" raises `PaymentImportError` |
| Every `frappe.throw` reached from `run_import` | ✅ only two (`reader.py:23`, `importer.py:62`), and both now raise `PaymentImportError` |

## Findings

### 1. ✅ Fixed — [Low] One malformed line fails the whole import with an unclear message
`formats.py:53-54`, `bcc_multipla.py:14-27`

This is older code, not part of this commit. `parse()` parses every line before the per-line
`try`, so a single bad amount or date stops the whole import. The user then sees a raw Python
message (checked in the console):
- bad amount → `[<class 'decimal.ConversionSyntax'>]`
- bad date → `time data '2026-08-06' does not match format '%d/%m/%Y'`

Because these are not `PaymentImportError`, the run is also logged as a bug. When TB-I2 adds more
readers, either turn a bad line into an `Error` row (as other failed lines are), or raise
`PaymentImportError` with the row number, e.g. "Row 12: invalid amount 'abc'".

### 2. ✅ Fixed — [Info] `PaymentImportError` lives in `reader.py`
The importer imports it from the reader. This is fine for now. If TB-I2 adds parsers that raise it,
consider moving it to `formats.py` or its own small module so parsers don't depend on the reader.

## Notes (no action)
- The `.gitignore` change and `references/payments/` are still uncommitted and were not reviewed.

---

# QA Review — `fa2f57c` fix(payment-import): clearer restart refusal, quieter error log, readable rows grid

**Status: ✅ DONE — finding 1 fixed in `31f9dfe`; finding 2 needs no change**

~~**Status: ⚠️ APPROVED WITH CHANGES REQUESTED**~~

Findings 2 and 3 from the `8f6aeb9` review are fixed. Finding 1 is fixed in a way that works for
user mistakes, but it also hides real failures (finding 1 below). That is a small change and should
be made before TB-I2.

## What was verified

| Check | Result |
|---|---|
| `test_payment_import` (12 tests) on `beb-test.localhost` | ✅ all pass (19.2 s) |
| `test_parsers` (11 tests) on `beb-test.localhost` | ✅ all pass |
| Old finding 1: rows grid on `site1.local` (agent-browser, `PAY-IMP-2026-0001`) | ✅ Posting Date, Amount, Result, Match Status and Bank Transaction are shown in full (no cell clipped, checked with `scrollWidth`); Payment Entry is no longer in the list view |
| Old finding 2: refusal wording | ✅ "The import is still running." while the job is alive; "This import has already been completed." for finished imports; both covered by tests |
| `RUNNING + STARTABLE` | ✅ both are tuples, so the concatenation is valid |
| Old finding 3: no Error Log for a wrong file | ✅ `test_unknown_file_fails_without_an_error_log` |

## Findings

### 1. ✅ Fixed — [Medium] Real failures in `complete()` are no longer logged
`importer.py:20`

`isinstance(error, frappe.ValidationError)` is broader than "user mistake". In Frappe these are all
subclasses of `ValidationError` (checked on this bench):
`TimestampMismatchError`, `MandatoryError`, `LinkValidationError`, `UniqueValidationError`,
`CharacterLengthExceededError`.

So the exact case from the `2001c54` review — someone saves the form during the run and
`complete()` raises `TimestampMismatchError` — now creates **no** Error Log entry. The same goes for
a schema or data bug that makes `save()` fail. Only the short `str(error)` is kept in
`error_message`, and there is no traceback for a developer to look at.

The new test does not catch this because it patches `complete` with a plain `Exception`
("Document modified"), which is not what Frappe would raise.

**Fix:** log unless the error is one that the importer raised itself. For example, raise a small
`PaymentImportError(frappe.ValidationError)` from `parse()` (and other expected `frappe.throw`
checks) and skip logging only for that class. Alternatively, check
`type(error) is frappe.ValidationError`. Change the test to use
`side_effect=frappe.TimestampMismatchError(...)` and assert `log_error` is called once.

### 2. [Info] The Restart button still shows during a healthy run
`payment_import.js:20-21`

This is acceptable now that the refusal says "The import is still running.", so no change is
needed. Noted only because the review offered two options and only the wording one was taken.

## Notes (no action)
- `validate_can_start` keeps the comment about a killed worker, which is still accurate.
- The `.gitignore` change and `references/payments/` are uncommitted and were not reviewed.

---

# QA Review — `8f6aeb9` fix(payment-import): recover failed and stuck imports, address TB-I1 review

**Status: ✅ DONE — findings 1–3 fixed**

~~**Status: ✅ APPROVED**~~ — all five findings from the `2001c54` review are fixed and verified. Ready
for TB-I2. The three new findings below are low severity and can go into TB-I2.

## What was verified

| Check | Result |
|---|---|
| `test_parsers` (11 tests) on `beb-test.localhost` | ✅ all pass |
| `test_payment_import` (11 tests) on `beb-test.localhost` | ✅ all pass (21.4 s) |
| `bench migrate` on `beb-test.localhost` (which had the previous schema) | ✅ CSV-only description and new grid columns synced |
| Old finding 1: stuck `Queued` import. Set `PAY-IMP-2026-0003` to `Queued` with no RQ job, opened it in the desk (agent-browser) | ✅ "Restart Import" button shown; clicking it ran the worker job → `Completed`, 58 rows / 58 Duplicate / 0 errors; polling reloaded the form |
| Old finding 1: failure outside the lines | ✅ `test_failure_outside_the_lines_marks_the_import_failed`: status `Failed`, error kept, no Bank Transactions left behind |
| `is_job_enqueued` vs `enqueue(job_id=…)` | ✅ both use `create_job_id`, so the site-prefixed ids match |
| Old finding 2: XLSX | ✅ `validate()` on a `.xlsx` gives "Only CSV files are supported."; the reader gives the same message |
| Old finding 3: fingerprint backward compatibility on `site1.local` | ✅ new `fingerprint()` over the `PAY-IMP-2026-0001` file matches **58/58** stored fingerprints, so existing data is not invalidated |
| Old finding 4: test gaps | ✅ posting fallback, ambiguous invoices, error row, withdrawal and restart are all covered |
| Old finding 5: progress / spec | ✅ `publish_progress` every 10 lines plus the last line; client hides it at 100 %. Spec `03` updated (Restart, progress, the `Queued` note) |
| No mid-run commits (needed for the outer savepoint) | ✅ none in the importer, the poster, or ERPNext's `bank_reconciliation_tool` / `bank_transaction` |

## Findings

### 1. ✅ Fixed — [Low / UX] The rows grid now cuts off Posting Date and Amount
`payment_import_row.json`

Result and Match now fit, but `posting_date` and `amount` are still 1 column each, so the desk shows
`06/0…` and `€ -5,00…`. Bank Transaction and Payment Entry are also cut off (`ACC-BTN-202…`). The
amount and date are what users scan for. One option: date 2, amount 2, result 2, match 2,
bank_transaction 2, and drop `payment_entry` from the list view (it can still be reached from the
row detail and the Bank Transaction).

### 2. ✅ Fixed — [Low / UX] "Restart Import" appears during every running import, even a healthy one
`payment_import.js:20-21`

The button is shown whenever the import is `Queued`/`In Progress`. While the job is alive, clicking
it gives "This import has already been started.", which is confusing for something labelled
*Restart*. Either give the server error a clearer wording for this case (e.g. "The import is still
running.") or show the button only after the import has stayed in a running state for a while
(e.g. `modified` older than the `long` queue timeout).

### 3. ✅ Fixed — [Info] User mistakes now also create Error Log entries
`importer.py:19`

`run_import` calls `frappe.log_error` for every failure, including expected `frappe.throw`
validations such as "Unrecognised file format". Each wrong upload adds an Error Log entry. Consider
logging only when the error is not a `frappe.ValidationError`.

## Notes (no action)
- The "Save" button stays active while an import is running. A save during the run now makes
  `complete()` fail cleanly (the whole run is rolled back and marked `Failed`, and it can be
  restarted), so this is no longer dangerous.
- `publish_progress` and the Restart button have no automated test. Both were checked by hand.
- If a worker is SIGKILLed, the RQ job can stay `started` until RQ cleans up its registry, so Restart
  may be refused for a few minutes. This is acceptable.

---

# QA Review — `2001c54` feat(payment-import): TB-I1 Multipla → exact match → Payment Entry

**Status: ✅ DONE — findings 1–5 fixed; 6–7 deferred to TB-I3 (see PROGRESS.md)**

~~**Status: ✅ APPROVED WITH CHANGES REQUESTED**~~ — TB-I1 meets its "Hit" criteria. One medium issue
(an import can get stuck for good) should be fixed before TB-I2. The other findings are low
severity or should be handled in later phases.

## What was verified

| Check | Result |
|---|---|
| `test_parsers` (10 tests) on `beb-test.localhost` | ✅ all pass |
| `test_payment_import` (5 tests) on `beb-test.localhost` | ✅ all pass (8.8 s) |
| e2e data on `site1.local`: `PAY-IMP-2026-0001` | ✅ 58 created / 1 reconciled / 57 unmatched / 0 errors; 58 Bank Transactions linked |
| Reconciled row | ✅ `ACC-BTN-2026-00003` (Reconciled, unallocated 0) → `ACC-PAY-2026-00008` (submitted, €345, MoP `Bonifico`, ref date 06/08) → `ACC-SINV-2026-00079` Paid |
| Re-import `PAY-IMP-2026-0002` | ✅ 0 created / 58 Duplicate |
| Desk (agent-browser): form, status badge, Results tab counts, rows grid | ✅ renders correctly, no Start button once Completed |
| Spec conformance (`01` TB-I1, `03`, `04` name rule) | ✅ apart from the items below |

## Findings

### 1. ✅ Fixed — [Medium] An import can get stuck in `Queued` with no way to recover
`importer.py:323-333`, `payment_import.py:159-174`

The job only catches errors from `parse()` and from each line. Anything raised outside those
blocks escapes the job. Examples: `complete()` → `save()` failing (`TimestampMismatchError` if
someone saves the form during the run, a validation error), a deadlock that wipes the savepoints
so `rollback(save_point=…)` itself raises, or the RQ worker timing out or being killed. Frappe's
`execute_job` then rolls back everything, including `db_set("status", "In Progress")`. The
document stays at the `Queued` status that `start_import` committed.

- `Queued` is not in `STARTABLE`, so `start_import` refuses to run again and no button is shown.
- The form polls every 3 s forever (`payment_import.js` `reload_when_done`).
- The only way out is to edit the database by hand.

**Fix:** wrap the whole `run()` so any failure ends in `fail()`, and commit that status in a
separate step. Alternatively, let `start_import` also accept a `Queued` or `In Progress` import
when its RQ job no longer exists. Add a test that makes `complete()` raise.

### 2. ✅ Fixed — [Low] Uploading an XLSX passes validation, then fails with a contradictory message
`payment_import.py:135,141` vs `reader.py:611-612`

`validate` accepts `.xlsx`, but `StatementReader.rows()` refuses anything that is not `.csv`,
and its error says *"Only CSV and XLSX files are supported."* The user uploads an XLSX and is told
XLSX is supported. XLSX is TB-I2 scope, so until then either limit `SUPPORTED_EXTENSIONS` to
`.csv` or make the reader say "XLSX is not supported yet".

### 3. ✅ Fixed — [Low] The fingerprint depends on how the amount is written
`importer.py:361-367`

`str(Decimal)` keeps the source's precision: `Decimal("345.00")` gives `345.00`, while an XLSX
float gives `345.0` or `345`. The same movement arriving through another reader would get a
different fingerprint. TB-I2 expects *"BCC Lista adds no duplicates over Multipla"*, and that will
fail for this reason alone (the descriptions may differ as well). Normalise the amount, for
example `line.amount.quantize(Decimal("0.01"))`, before TB-I2 adds more readers. Changing it later
would invalidate the fingerprints already stored on `site1.local`.

### 4. ✅ Fixed — [Low] Test gaps on the riskiest paths
These branches have no test:
- a posting failure falling back to `Suggested` with the "Posting failed" reason (`importer.py:399-406`)
- two invoices with the same customer and amount → `Unmatched`, not an arbitrary pick (`matcher.py:461`)
- one bad line → `Error` row while the other lines still import (`importer.py:357-359`)
- a withdrawal never being matched

Finding 1 also needs a regression test.

### 5. ✅ Fixed — [Low / UX] Spec items not delivered or not visible
- Spec `03 §1` says "Progress via `frappe.publish_progress`". Nothing is published, so a long
  file shows only the "Importing…" headline.
- Because the job never commits, `In Progress` is never visible to users. The form shows
  `Queued` until the end. This matches the note in `03 §1` but makes the `In Progress` option
  and the `RUNNING` check in the JS effectively dead. Consider dropping the state or documenting
  it in the spec.
- The rows grid has 8 list-view columns, so Result and Match values are cut off
  ("Crea…", "Unm…"). Consider moving `description` or `value_date` out of the list view.

### 6. ⏭ Deferred to TB-I3 — [Info] Payment Entry `reference_no` is a cut-off description
When a line has no End-to-End ID or RIF (as with the Franco Ferri transfer), `reference_no`
becomes the first 140 characters of the description (`ACC-PAY-2026-00008` shows
`Ordinante: FRANCO FERRI … Indir`). This follows the spec, but it is noisy in reports. Consider
`payer_name + posting date` instead.

### 7. ⏭ Deferred to TB-I3 — [Info] Name matching uses the whole description
This follows spec `04` (tokens in `bank_party_name` + description), but certain matches are
posted automatically. A short customer name whose tokens show up in the address or reason text
(e.g. a customer "Ceraso" against `VIA CERASO 1`) could auto-post against the wrong customer when
the amount happens to match. Keep this in mind when TB-I3 adds rules. Limiting the *certain*
rule to `bank_party_name` would be safer.

## Code quality
The code is clean and object-oriented (Reader / Parser / Signals / Importer / Matcher / Poster),
functions are small, and it reuses ERPNext's `create_payment_entry_and_reconcile` and
`get_payment_entry`. The fingerprint has a unique constraint and the import link is indexed.
`set_only_once` is set on company and bank account, and changing the file after the import is
blocked both on the server and in the form. No security issues were found beyond the standard
Frappe permissions.
