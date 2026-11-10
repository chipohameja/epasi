import frappe
from frappe import _
from frappe.utils import date_diff, today

UNPAID_STATUSES = ["Active", "Overdue", "Defaulted"]
LOAN_FIELDS = ["name", "borrower", "borrower_name", "whatsapp_number", "status", "due_date", "total_due", "outstanding"]


def execute(filters=None):
	return get_columns(), get_data(filters or {})


def get_data(filters: dict) -> list[dict]:
	loan_filters = {"docstatus": 1, "status": filters.get("status") or ["in", UNPAID_STATUSES]}
	loans = frappe.get_all("Loan", filters=loan_filters, fields=LOAN_FIELDS, order_by="due_date asc")
	for loan in loans:
		loan.days_overdue = max(date_diff(today(), loan.due_date), 0)
	return loans


def get_columns() -> list[dict]:
	return [
		{"fieldname": "name", "label": _("Loan"), "fieldtype": "Link", "options": "Loan", "width": 120},
		{"fieldname": "borrower_name", "label": _("Borrower"), "fieldtype": "Data", "width": 180},
		{"fieldname": "whatsapp_number", "label": _("WhatsApp"), "fieldtype": "Data", "width": 130},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
		{"fieldname": "due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "days_overdue", "label": _("Days Overdue"), "fieldtype": "Int", "width": 110},
		{"fieldname": "total_due", "label": _("Total Due"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "outstanding", "label": _("Outstanding"), "fieldtype": "Currency", "width": 130},
	]
