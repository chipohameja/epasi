import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, fmt_money


class LoanRepayment(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be more than zero"))

	def before_submit(self):
		loan = self.get_loan()
		if loan.docstatus != 1 or loan.status == "Closed":
			frappe.throw(_("Loan {0} is not open for repayment").format(loan.name))
		if flt(self.amount) > flt(loan.outstanding):
			frappe.throw(_("Amount is more than the outstanding balance of {0}").format(fmt_money(loan.outstanding)))
		self.interest_portion = min(flt(self.amount), loan.interest_due)
		self.principal_portion = flt(self.amount) - self.interest_portion

	def on_submit(self):
		self.get_loan().update_paid_amounts()

	def on_cancel(self):
		self.get_loan().update_paid_amounts()

	def get_loan(self):
		return frappe.get_doc("Loan", self.loan, for_update=True)
