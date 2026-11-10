import frappe
from frappe import _
from frappe.utils import getdate

from epasi.epasi.money import EXPENSES, INTEREST, RECOVERY, MoneySummary

COLUMNS = {"interest_collected": INTEREST, "recovery_income": RECOVERY, "expenses": EXPENSES}


def execute(filters=None):
	report = ProfitSummary(filters or {})
	return report.get_columns(), report.get_data(), None, None, report.get_summary()


class ProfitSummary:
	def __init__(self, filters: dict):
		self.from_date = getdate(filters.get("from_date"))
		self.to_date = getdate(filters.get("to_date"))
		if self.from_date > self.to_date:
			frappe.throw(_("From Date must be before To Date"))

	def get_data(self) -> list[dict]:
		totals = {column: ledger.by_date(self.from_date, self.to_date) for column, ledger in COLUMNS.items()}
		days = sorted(set().union(*totals.values()))
		return [self.get_row(day, totals) for day in days]

	def get_row(self, day, totals: dict) -> dict:
		row = {"date": day, **{column: totals[column].get(day, 0) for column in COLUMNS}}
		row["net_profit"] = row["interest_collected"] + row["recovery_income"] - row["expenses"]
		return row

	def get_summary(self) -> list[dict]:
		summary = MoneySummary(self.from_date, self.to_date)
		net_indicator = "Green" if summary.net_profit >= 0 else "Red"
		return [
			{"label": _("Interest Collected"), "value": summary.interest_collected, "datatype": "Currency"},
			{"label": _("Recovery Income"), "value": summary.recovery_income, "datatype": "Currency"},
			{"label": _("Expenses"), "value": summary.expenses, "datatype": "Currency", "indicator": "Red"},
			{"label": _("Net Profit"), "value": summary.net_profit, "datatype": "Currency", "indicator": net_indicator},
		]

	def get_columns(self) -> list[dict]:
		labels = {
			"interest_collected": _("Interest Collected"),
			"recovery_income": _("Recovery Income"),
			"expenses": _("Expenses"),
			"net_profit": _("Net Profit"),
		}
		columns = [{"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 120}]
		return columns + [
			{"fieldname": name, "label": label, "fieldtype": "Currency", "width": 160} for name, label in labels.items()
		]
