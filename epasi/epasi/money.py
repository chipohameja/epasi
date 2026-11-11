from dataclasses import dataclass, field
from functools import cached_property

import frappe
from frappe.utils import flt, getdate


@dataclass(frozen=True)
class Ledger:
	"""Sums one money column of a DocType over a date range."""

	doctype: str
	amount_field: str
	date_field: str
	filters: dict = field(default_factory=dict)

	def total(self, from_date, to_date) -> float:
		rows = frappe.get_all(
			self.doctype,
			filters=self.get_filters(from_date, to_date),
			fields=[{"SUM": self.amount_field, "as": "total"}],
		)
		return flt(rows[0].total)

	def by_date(self, from_date, to_date) -> dict:
		rows = frappe.get_all(
			self.doctype,
			filters=self.get_filters(from_date, to_date),
			fields=[self.date_field, {"SUM": self.amount_field, "as": "total"}],
			group_by=self.date_field,
		)
		return {getdate(row[self.date_field]): flt(row.total) for row in rows}

	def get_filters(self, from_date, to_date) -> dict:
		return {**self.filters, self.date_field: ["between", [from_date, to_date]]}


LENT = Ledger("Loan", "principal", "disbursement_date", {"docstatus": 1})
COLLECTED = Ledger("Loan Repayment", "amount", "payment_date", {"docstatus": 1})
INTEREST = Ledger("Loan Repayment", "interest_portion", "payment_date", {"docstatus": 1})
RECOVERY = Ledger("Collateral", "sale_amount", "sale_date", {"status": "Sold"})
EXPENSES = Ledger("Expense", "amount", "expense_date")
COMMISSION_PAID = Ledger("Commission", "amount", "paid_date", {"status": "Paid"})


class MoneySummary:
	"""Profit = interest collected + collateral recovery - expenses."""

	def __init__(self, from_date, to_date):
		self.from_date, self.to_date = from_date, to_date

	@cached_property
	def interest_collected(self) -> float:
		return INTEREST.total(self.from_date, self.to_date)

	@cached_property
	def recovery_income(self) -> float:
		return RECOVERY.total(self.from_date, self.to_date)

	@cached_property
	def expenses(self) -> float:
		return EXPENSES.total(self.from_date, self.to_date)

	@property
	def net_profit(self) -> float:
		return self.interest_collected + self.recovery_income - self.expenses
