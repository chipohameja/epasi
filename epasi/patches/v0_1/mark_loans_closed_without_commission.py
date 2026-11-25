import frappe


def execute():
	loan = frappe.qb.DocType("Loan")
	commission = frappe.qb.DocType("Commission")
	paid_loans = frappe.qb.from_(commission).select(commission.loan)
	frappe.qb.update(loan).set(loan.closed_without_commission, 1).where(
		(loan.docstatus == 1)
		& (loan.status == "Closed")
		& loan.sales_agent.isnotnull()
		& loan.name.notin(paid_loans)
	).run()
