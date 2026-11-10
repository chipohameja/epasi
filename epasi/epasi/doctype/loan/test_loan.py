import frappe
from frappe.tests import IntegrationTestCase

from epasi.tests.utils import make_loan


class TestLoan(IntegrationTestCase):
	def test_two_weeks_plan_totals(self):
		loan = make_loan("2 Weeks", 1000, "2026-11-01")
		self.assertEqual((loan.interest_rate, loan.term_days), (27, 14))
		self.assertEqual((loan.interest_amount, loan.total_due, loan.outstanding), (270, 1270, 1270))
		self.assertEqual(str(loan.due_date), "2026-11-15")

	def test_one_month_plan_totals(self):
		loan = make_loan("1 Month", 2500, "2026-11-01")
		self.assertEqual((loan.interest_amount, loan.total_due), (1000, 3500))
		self.assertEqual(str(loan.due_date), "2026-12-01")

	def test_rate_snapshot_ignores_plan_changes(self):
		loan = make_loan("2 Weeks")
		self.addCleanup(frappe.db.set_value, "Loan Plan", "2 Weeks", {"interest_rate": 27, "term_days": 14})
		frappe.db.set_value("Loan Plan", "2 Weeks", {"interest_rate": 50, "term_days": 7})
		loan.reload()
		loan.save()
		self.assertEqual((loan.interest_rate, loan.term_days, loan.total_due), (27, 14, 1270))

	def test_principal_must_be_positive(self):
		self.assertRaises(frappe.ValidationError, make_loan, principal=0)
