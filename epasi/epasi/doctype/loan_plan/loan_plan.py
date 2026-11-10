import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import fmt_money


class LoanPlan(Document):
	def validate(self):
		if self.minimum_amount > self.maximum_amount:
			frappe.throw(_("Minimum Amount cannot be more than Maximum Amount"))

	def validate_amount(self, amount: float):
		if not self.is_active:
			frappe.throw(_("Loan Plan {0} is not available").format(self.name))
		if not self.minimum_amount <= amount <= self.maximum_amount:
			frappe.throw(
				_("Amount for {0} must be between {1} and {2}").format(
					self.name, fmt_money(self.minimum_amount), fmt_money(self.maximum_amount)
				)
			)
