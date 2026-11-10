import frappe
from frappe.tests import IntegrationTestCase

from epasi.api.public import get_loan_plans, submit_application
from epasi.tests.utils import make_photo


def apply(whatsapp_number: str = "0972000001", amount: float = 1000, **details) -> str:
	return submit_application(
		full_name="Guest Applicant",
		whatsapp_number=whatsapp_number,
		loan_plan="2 Weeks",
		amount=amount,
		photos=[make_photo()],
		**details,
	)["name"]


class TestPublicApi(IntegrationTestCase):
	def setUp(self):
		frappe.set_user("Guest")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_get_loan_plans_returns_active_plans(self):
		plans = {plan.name: plan for plan in get_loan_plans()}
		self.assertEqual(plans["2 Weeks"].interest_rate, 27)
		self.assertEqual(plans["1 Month"].interest_rate, 40)

	def test_guest_can_submit_application_with_collateral(self):
		name = apply(purpose="Business", collateral_description="Fridge", estimated_value=3000)
		application = frappe.get_doc("Loan Application", name)
		self.assertEqual(application.borrower, "260972000001")
		self.assertEqual(application.status, "Pending")
		self.assertEqual((application.purpose, application.estimated_value), ("Business", 3000))
		self.assertEqual(frappe.db.count("File", {"attached_to_name": name, "is_private": 1}), 1)

	def test_borrower_details_are_saved_and_kept(self):
		apply(whatsapp_number="0972000003", nrc_number="123456/10/1", address="Mazabuka")
		apply(whatsapp_number="0972000003")
		borrower = frappe.get_doc("Borrower", "260972000003")
		self.assertEqual((borrower.nrc_number, borrower.address), ("123456/10/1", "Mazabuka"))

	def test_amount_outside_plan_limits_is_rejected(self):
		maximum = frappe.db.get_value("Loan Plan", "2 Weeks", "maximum_amount")
		self.assertRaises(frappe.ValidationError, apply, whatsapp_number="0972000002", amount=maximum + 1)

	def test_application_without_photos_is_rejected(self):
		self.assertRaises(
			frappe.ValidationError, submit_application, "Guest Applicant", "0972000004", "2 Weeks", 1000, []
		)
