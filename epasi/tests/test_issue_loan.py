import frappe
from frappe.tests import IntegrationTestCase

from epasi.tests.utils import make_application


class TestIssueLoan(IntegrationTestCase):
	def test_create_loan_from_approved_application(self):
		application = frappe.get_doc("Loan Application", make_application("1 Month", 2000))
		loan = frappe.get_doc("Loan", application.create_loan())
		self.assertEqual((loan.docstatus, loan.borrower, loan.principal), (0, application.borrower, 2000))
		self.assertEqual(loan.total_due, 2800)

	def test_pending_application_cannot_create_loan(self):
		application = frappe.get_doc("Loan Application", make_application(status="Pending"))
		self.assertRaises(frappe.ValidationError, application.create_loan)

	def test_second_loan_for_same_application_is_rejected(self):
		application = frappe.get_doc("Loan Application", make_application())
		application.create_loan()
		self.assertRaises(frappe.ValidationError, application.create_loan)

	def test_submit_creates_held_collateral_with_photos(self):
		application = frappe.get_doc("Loan Application", make_application())
		loan = frappe.get_doc("Loan", application.create_loan())
		loan.submit()
		collateral = frappe.get_doc("Collateral", {"loan": loan.name})
		self.assertEqual((collateral.status, collateral.description), ("Held", "Television"))
		self.assertEqual(collateral.estimated_value, 2500)
		photos = frappe.get_all("File", {"attached_to_doctype": "Collateral", "attached_to_name": collateral.name})
		self.assertEqual(len(photos), 1)
