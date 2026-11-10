from dataclasses import dataclass

import frappe
from frappe import _
from frappe.utils import flt, getdate


@dataclass(frozen=True)
class Activity:
	label: str
	doctype: str
	date_field: str
	party_field: str
	details_field: str
	amount_field: str
	filters: tuple = ()

	def get_rows(self, date) -> list[dict]:
		records = frappe.get_all(
			self.doctype,
			filters={**dict(self.filters), self.date_field: ["between", [date, date]]},
			fields=["name", self.party_field, self.details_field, self.amount_field],
			order_by="creation asc",
		)
		return [self.to_row(record) for record in records]

	def to_row(self, record) -> dict:
		return {
			"activity": self.label,
			"document_type": self.doctype,
			"document": record.name,
			"party": record[self.party_field],
			"details": record[self.details_field],
			"amount": flt(record[self.amount_field]),
		}


ACTIVITIES = (
	Activity("Application", "Loan Application", "creation", "applicant_name", "loan_plan", "amount"),
	Activity("Disbursement", "Loan", "disbursement_date", "borrower_name", "loan_plan", "principal", (("docstatus", 1),)),
	Activity("Repayment", "Loan Repayment", "payment_date", "borrower_name", "mode", "amount", (("docstatus", 1),)),
	Activity("Expense", "Expense", "expense_date", "category", "description", "amount"),
)


def execute(filters=None):
	date = getdate((filters or {}).get("date"))
	rows_by_activity = {activity.label: activity.get_rows(date) for activity in ACTIVITIES}
	data = [row for rows in rows_by_activity.values() for row in rows]
	return get_columns(), data, None, None, get_summary(rows_by_activity)


def get_summary(rows_by_activity: dict) -> list[dict]:
	return [
		{
			"label": _("{0}s ({1})").format(_(label), len(rows)),
			"value": sum(row["amount"] for row in rows),
			"datatype": "Currency",
			"indicator": "Red" if label == "Expense" else "Blue",
		}
		for label, rows in rows_by_activity.items()
	]


def get_columns() -> list[dict]:
	return [
		{"fieldname": "activity", "label": _("Activity"), "fieldtype": "Data", "width": 120},
		{"fieldname": "document_type", "label": _("Type"), "fieldtype": "Link", "options": "DocType", "hidden": 1},
		{"fieldname": "document", "label": _("Document"), "fieldtype": "Dynamic Link", "options": "document_type", "width": 130},
		{"fieldname": "party", "label": _("Party"), "fieldtype": "Data", "width": 180},
		{"fieldname": "details", "label": _("Details"), "fieldtype": "Data", "width": 200},
		{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 130},
	]
