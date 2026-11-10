import frappe
from frappe import _
from frappe.model.document import Document


class LoanApplication(Document):
	def validate(self):
		frappe.get_doc("Loan Plan", self.loan_plan).validate_amount(self.amount)

	@frappe.whitelist()
	def create_loan(self) -> str:
		self.check_permission("write")
		if self.status != "Approved":
			frappe.throw(_("Approve the application before you create a loan"))
		if existing := frappe.db.exists("Loan", {"loan_application": self.name, "docstatus": ["<", 2]}):
			frappe.throw(_("Loan {0} already exists for this application").format(existing))
		loan = frappe.get_doc(
			doctype="Loan",
			borrower=self.borrower,
			loan_application=self.name,
			loan_plan=self.loan_plan,
			principal=self.amount,
		)
		return loan.insert().name
