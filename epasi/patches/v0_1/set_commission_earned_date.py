import frappe
from frappe.query_builder.functions import Date


def execute():
	commission = frappe.qb.DocType("Commission")
	frappe.qb.update(commission).set(commission.earned_date, Date(commission.creation)).where(
		commission.earned_date.isnull()
	).run()
