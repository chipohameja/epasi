import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, flt, getdate, today

from epasi.epasi.doctype.collateral.collateral import Collateral
from epasi.epasi.doctype.commission.commission import Commission

OPEN_STATUSES = ("Active", "Overdue")


class Loan(Document):
	def validate(self):
		if flt(self.principal) <= 0:
			frappe.throw(_("Principal must be more than zero"))
		if self.has_value_changed("loan_plan"):
			self.copy_plan_terms()
		self.calculate_totals()

	def before_submit(self):
		self.sales_agent = self.sales_agent or frappe.db.get_value("Borrower", self.borrower, "sales_agent")
		if self.sales_agent:
			self.commission_rate, self.minimum_principal = frappe.db.get_value(
				"Sales Agent", self.sales_agent, ["commission_rate", "minimum_principal"]
			)

	def on_submit(self):
		if self.loan_application:
			Collateral.create_from_loan(self)
		self.update_borrower_totals()

	def on_cancel(self):
		self.update_borrower_totals()

	def copy_plan_terms(self):
		self.interest_rate, self.term_days = frappe.db.get_value(
			"Loan Plan", self.loan_plan, ["interest_rate", "term_days"]
		)

	def calculate_totals(self):
		self.due_date = add_days(self.disbursement_date, self.term_days)
		self.interest_amount = flt(
			self.principal * self.interest_rate / 100, self.precision("interest_amount")
		)
		self.total_due = flt(self.principal) + self.interest_amount
		self.outstanding = self.total_due - flt(self.interest_paid) - flt(self.principal_paid)
		self.status = self.get_status()

	def get_status(self) -> str:
		if self.docstatus == 1 and flt(self.outstanding) <= 0:
			return "Closed"
		if self.status == "Defaulted":
			return "Defaulted"
		return "Overdue" if getdate(self.due_date) < getdate(today()) else "Active"

	@property
	def interest_due(self) -> float:
		return flt(self.interest_amount) - flt(self.interest_paid)

	def update_paid_amounts(self):
		self.interest_paid, self.principal_paid = self.get_repaid_totals()
		self.calculate_totals()
		self.save()
		self.update_borrower_totals()
		Commission.sync_for_loan(self)

	def get_repaid_totals(self) -> tuple[float, float]:
		repayment = frappe.qb.DocType("Loan Repayment")
		totals = (
			frappe.qb.from_(repayment)
			.select(Sum(repayment.interest_portion), Sum(repayment.principal_portion))
			.where((repayment.loan == self.name) & (repayment.docstatus == 1))
			.run()[0]
		)
		return flt(totals[0]), flt(totals[1])

	@frappe.whitelist()
	def mark_defaulted(self):
		self.check_permission("write")
		if self.docstatus != 1 or self.status not in OPEN_STATUSES:
			frappe.throw(_("Only an active or overdue loan can be marked as defaulted"))
		self.db_set("status", "Defaulted")
		Collateral.forfeit_for_loan(self.name)

	def update_borrower_totals(self):
		frappe.get_doc("Borrower", self.borrower).update_totals()


def mark_overdue_loans():
	frappe.db.set_value(
		"Loan",
		{"docstatus": 1, "status": "Active", "due_date": ["<", today()]},
		"status",
		"Overdue",
	)
