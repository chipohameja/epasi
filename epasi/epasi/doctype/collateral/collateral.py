import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from epasi.epasi.collateral_photos import copy_photos
from epasi.epasi.money import RECOVERY

NEXT_STATUSES = {
	"With Borrower": ("Held", "Returned", "Forfeited"),
	"Held": ("With Borrower", "Returned", "Forfeited"),
	"Forfeited": ("Sold", "Returned"),
	"Returned": (),
	"Sold": (),
}
REQUIRED_LOAN_STATUS = {"Forfeited": "Defaulted", "Returned": "Closed"}


class Collateral(Document):
	def validate(self):
		if self.has_value_changed("status") and not self.is_new():
			self.validate_status_change()
		if self.status == "Sold" and (not self.sale_date or flt(self.sale_amount) <= 0):
			frappe.throw(_("Enter the sale date and sale amount for sold collateral"))

	def validate_status_change(self):
		previous = self.get_doc_before_save().status
		if self.status not in NEXT_STATUSES[previous]:
			frappe.throw(_("Collateral cannot move from {0} to {1}").format(previous, self.status))
		loan_status = REQUIRED_LOAN_STATUS.get(self.status)
		if self.loan and loan_status and frappe.db.get_value("Loan", self.loan, "status") != loan_status:
			frappe.throw(_("Collateral can be {0} only when its loan is {1}").format(self.status, loan_status))

	@staticmethod
	def create_from_loan(loan: Document) -> "Collateral":
		application = frappe.get_doc("Loan Application", loan.loan_application)
		collateral = frappe.get_doc(
			doctype="Collateral",
			borrower=loan.borrower,
			loan=loan.name,
			description=application.collateral_description or _("Not described"),
			estimated_value=application.estimated_value,
			status="Held",
		).insert()
		copy_photos("Loan Application", application.name, "Collateral", collateral.name)
		return collateral

	@staticmethod
	def forfeit_for_loan(loan: str):
		filters = {"loan": loan, "status": ["in", ["With Borrower", "Held"]]}
		for name in frappe.get_all("Collateral", filters=filters, pluck="name"):
			collateral = frappe.get_doc("Collateral", name)
			collateral.status = "Forfeited"
			collateral.save()


def get_recovery_income(from_date: str, to_date: str) -> float:
	return RECOVERY.total(from_date, to_date)
