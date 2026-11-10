import frappe
from frappe.tests import IntegrationTestCase


class TestLoanPlan(IntegrationTestCase):
	def test_seeded_plans(self):
		self.assertEqual(frappe.db.get_value("Loan Plan", "2 Weeks", ["interest_rate", "term_days"]), (27, 14))
		self.assertEqual(frappe.db.get_value("Loan Plan", "1 Month", ["interest_rate", "term_days"]), (40, 30))

	def test_minimum_above_maximum_is_rejected(self):
		plan = frappe.get_doc("Loan Plan", "2 Weeks")
		plan.minimum_amount = plan.maximum_amount + 1
		self.assertRaises(frappe.ValidationError, plan.save)

	def test_inactive_plan_rejects_amount(self):
		plan = frappe.get_doc("Loan Plan", "2 Weeks")
		plan.is_active = 0
		self.assertRaises(frappe.ValidationError, plan.validate_amount, plan.minimum_amount)
