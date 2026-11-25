import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class Commission(Document):
	def validate(self):
		self.amount = flt(flt(self.interest_paid) * flt(self.commission_rate) / 100, self.precision("amount"))

	def on_update(self):
		self.update_agent_totals()

	def after_delete(self):
		self.update_agent_totals()

	def update_agent_totals(self):
		frappe.get_doc("Sales Agent", self.sales_agent).update_commission_totals()

	@frappe.whitelist()
	def mark_paid(self):
		self.check_permission("write")
		if self.status == "Paid":
			frappe.throw(_("Commission {0} is already paid").format(self.name))
		self.expense = self.create_expense()
		self.status, self.paid_date = "Paid", today()
		self.save()

	def create_expense(self) -> str:
		agent_name = frappe.db.get_value("Sales Agent", self.sales_agent, "full_name")
		description = _("Commission {0} for {1} on loan {2}").format(self.name, agent_name, self.loan)
		expense = frappe.get_doc(
			doctype="Expense",
			expense_date=today(),
			category="Commission",
			amount=self.amount,
			description=description,
		)
		return expense.insert().name

	@staticmethod
	def sync_for_agent(sales_agent: str | None):
		if not sales_agent:
			return
		filters = {"sales_agent": sales_agent, "docstatus": 1, "status": "Closed"}
		for loan in frappe.get_all("Loan", filters=filters, pluck="name"):
			Commission.sync_for_loan(frappe.get_doc("Loan", loan))

	@staticmethod
	def sync_for_loan(loan: Document):
		existing = frappe.db.get_value("Commission", {"loan": loan.name}, ["name", "status"], as_dict=True)
		earns = loan.status == "Closed" and earns_commission(loan)
		if earns and not existing:
			Commission.create_for_loan(loan)
		elif not earns and existing and existing.status == "Unpaid":
			frappe.delete_doc("Commission", existing.name, ignore_permissions=True)

	@staticmethod
	def create_for_loan(loan: Document):
		frappe.get_doc(
			doctype="Commission",
			sales_agent=loan.sales_agent,
			loan=loan.name,
			borrower=loan.borrower,
			principal=loan.principal,
			interest_paid=loan.interest_paid,
			commission_rate=loan.commission_rate,
			earned_date=today(),
		).insert(ignore_permissions=True)


def earns_commission(loan: Document) -> bool:
	if not loan.sales_agent or flt(loan.commission_rate) <= 0 or loan.closed_without_commission:
		return False
	return get_agent_principal(loan.sales_agent) >= flt(loan.minimum_principal)


def get_agent_principal(sales_agent: str) -> float:
	filters = {"sales_agent": sales_agent, "docstatus": 1}
	rows = frappe.get_all("Loan", filters=filters, fields=[{"SUM": "principal", "as": "total"}])
	return flt(rows[0].total)
