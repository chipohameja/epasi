import frappe
from frappe import _
from frappe.model.document import Document

from epasi.epasi.doctype.sales_agent.sales_agent import SalesAgent


class LoanApplication(Document):
	def validate(self):
		if self.is_new():
			self.set_sales_agent()
		frappe.get_doc("Loan Plan", self.loan_plan).validate_amount(self.amount)

	def on_update(self):
		if self.sales_agent and not frappe.db.get_value("Borrower", self.borrower, "sales_agent"):
			frappe.db.set_value("Borrower", self.borrower, "sales_agent", self.sales_agent)

	def set_sales_agent(self):
		borrower_agent = frappe.db.get_value("Borrower", self.borrower, "sales_agent")
		self.sales_agent = (
			borrower_agent or self.sales_agent or SalesAgent.for_user(agent_type="Loan Officer")
		)

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
			sales_agent=self.sales_agent,
		)
		return loan.insert().name
